"""
Single-worker pipeline runner.

Why single-worker
-----------------
`google-generativeai` is configured globally (`genai.configure(api_key=...)`)
inside `core/llm_client.py`. Two pipelines from different users running in
parallel would race on that global, so the backend serialises runs through
one worker. Concurrency knob lives in `max_concurrent` for future migration
to a per-instance SDK without rewriting the call sites.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional

from agents.coordinator_llm import LLMCoordinatorAgent
from backend.events import EventEmitter

log = logging.getLogger(__name__)


class RunNotFound(Exception):
    pass


@dataclass
class RunState:
    run_id: str
    emitter: EventEmitter
    status: str = "queued"  # queued | running | done | error | cancelled
    error: Optional[str] = None


@dataclass
class _Job:
    run_id: str
    filepath: str
    api_key: str
    output_path: str


class PipelineRunner:
    def __init__(self, max_concurrent: int = 1):
        self.max_concurrent = max_concurrent
        self._queue: asyncio.Queue[_Job] = asyncio.Queue()
        self._runs: Dict[str, RunState] = {}
        self._cancel_flags: Dict[str, bool] = {}
        self._workers: list[asyncio.Task] = []

    @property
    def queue_size(self) -> int:
        return self._queue.qsize()

    async def start(self) -> None:
        for i in range(self.max_concurrent):
            self._workers.append(asyncio.create_task(self._worker(), name=f"pipeline-worker-{i}"))

    async def stop(self) -> None:
        for w in self._workers:
            w.cancel()
        for w in self._workers:
            try:
                await w
            except (asyncio.CancelledError, Exception):
                pass
        self._workers.clear()

    async def submit(self, run_id: str, filepath: str, api_key: str, output_path: str) -> EventEmitter:
        if run_id in self._runs:
            raise ValueError(f"run_id {run_id} already submitted")
        emitter = EventEmitter(run_id)
        self._runs[run_id] = RunState(run_id=run_id, emitter=emitter, status="queued")
        await self._queue.put(_Job(run_id=run_id, filepath=filepath, api_key=api_key, output_path=output_path))
        return emitter

    def get_emitter(self, run_id: str) -> EventEmitter:
        state = self._runs.get(run_id)
        if state is None:
            raise RunNotFound(run_id)
        return state.emitter

    def get_state(self, run_id: str) -> RunState:
        state = self._runs.get(run_id)
        if state is None:
            raise RunNotFound(run_id)
        return state

    def set_cancel(self, run_id: str) -> bool:
        if run_id not in self._runs:
            return False
        self._cancel_flags[run_id] = True
        return True

    def get_queue_position(self, run_id: str) -> Optional[int]:
        """Position in the queued runs (0 = next to run), or None if the run
        is not queued. Relies on Python 3.7+ dict insertion order."""
        state = self._runs.get(run_id)
        if state is None or state.status != "queued":
            return None
        pos = 0
        for rid, rs in self._runs.items():
            if rid == run_id:
                return pos
            if rs.status == "queued":
                pos += 1
        return pos

    async def _worker(self) -> None:
        while True:
            job = await self._queue.get()
            state = self._runs[job.run_id]

            if self._cancel_flags.get(job.run_id):
                state.status = "cancelled"
                await state.emitter.emit("error", {"message": "cancelled before start"})
                await state.emitter.close()
                continue

            state.status = "running"
            try:
                coordinator = LLMCoordinatorAgent(
                    api_key=job.api_key,
                    event_emitter=state.emitter,
                )
                await coordinator.execute_pipeline(job.filepath, output_path=job.output_path)
                state.status = "done"
            except Exception as exc:
                log.exception("pipeline failed for run %s", job.run_id)
                state.status = "error"
                state.error = str(exc)
                # The coordinator already emitted an `error` event on its way
                # out, but we emit again here to cover failures originating
                # outside execute_pipeline (e.g. import errors).
                await state.emitter.emit("error", {"message": str(exc)})
            finally:
                await state.emitter.close()
