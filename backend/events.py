"""
Per-run event sink shared between the pipeline (producer) and the SSE
endpoint (consumer).

Contract
--------
Event types emitted by LLMCoordinatorAgent:

    pipeline.start  { file, output_path }
    agent.start     { agent }
    agent.end       { agent, summary }
    pipeline.end    { output_path, report_status }
    error           { message }

`pipeline.end` and `error` are terminal: after one of them the stream
ends and consumers should stop polling.
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import AsyncIterator, Dict, Any


TERMINAL_EVENTS = ("pipeline.end", "error")


class EventEmitter:
    """Single-producer / single-consumer event queue for one pipeline run."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self._queue: asyncio.Queue = asyncio.Queue()
        self._closed = False

    async def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        if self._closed:
            return
        envelope = {
            "type": event_type,
            "ts": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
            "data": data,
        }
        await self._queue.put(envelope)

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        await self._queue.put(None)

    async def stream(self) -> AsyncIterator[str]:
        """Yield SSE-formatted chunks. Returns when a terminal event or
        close() sentinel is consumed."""
        while True:
            envelope = await self._queue.get()
            if envelope is None:
                return
            payload = json.dumps(envelope, ensure_ascii=False)
            yield f"event: {envelope['type']}\ndata: {payload}\n\n"
            if envelope["type"] in TERMINAL_EVENTS:
                return
