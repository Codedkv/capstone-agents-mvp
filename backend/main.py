"""
Outlier backend — FastAPI wrapper around the 5-agent pipeline.

Run locally:
    uvicorn backend.main:app --reload --port 8000

Endpoints
---------
    GET  /api/health              -> liveness + queue size
    POST /api/validate_key        -> body: {api_key}, lightweight Gemini ping
    POST /api/upload              -> multipart upload, returns {run_id, ...}
    POST /api/run/{run_id}        -> body: {api_key}, kicks off pipeline
    GET  /api/state/{run_id}      -> current run status (no SSE attach)
    GET  /api/events/{run_id}     -> SSE stream of pipeline events
    GET  /api/report/{run_id}     -> HTML report (when pipeline done)
    POST /api/cancel/{run_id}     -> request cancellation (best-effort)
"""

import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, UploadFile, HTTPException, Request, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend import storage
from backend.runner import PipelineRunner, RunNotFound


limiter = Limiter(key_func=get_remote_address)
runner = PipelineRunner(max_concurrent=1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await runner.start()
    try:
        yield
    finally:
        await runner.stop()


app = FastAPI(title="Outlier API", version="0.1.0", lifespan=lifespan)
app.state.limiter = limiter

# CORS — Next.js dev origins. Production origin is added once the frontend
# domain is provisioned (Phase 3).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"error": "rate limit exceeded"})


# --- Schemas ---------------------------------------------------------------


class RunRequest(BaseModel):
    # repr=False keeps the api_key out of any debug repr / log line that
    # accidentally formats the model.
    # Gemini API keys begin with "AIza" and are ~39 chars long.
    api_key: str = Field(..., min_length=30, max_length=200, repr=False)


# --- Routes ----------------------------------------------------------------


@app.get("/api/health")
async def health():
    return {"status": "ok", "queue_size": runner.queue_size}


@app.post("/api/validate_key")
@limiter.limit("20/minute")
async def validate_key(body: RunRequest, request: Request):
    """Lightweight check that the supplied Gemini key is accepted by Google.

    Uses the public REST `models.list` endpoint instead of the SDK so we
    don't mutate the process-global `genai.configure()` while the pipeline
    runner might be using a different key for an in-flight run.

    Response codes:
        200 — {"valid": true}
        401 — {"valid": false, "reason": "invalid_key"}
        429 — {"valid": false, "reason": "rate_limited"} (key works but throttled)
        500 — {"valid": false, "reason": "<network|timeout|upstream_error>"}
    """
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(url, params={"key": body.api_key})
    except httpx.TimeoutException:
        return JSONResponse(status_code=500, content={"valid": False, "reason": "timeout"})
    except httpx.RequestError as exc:
        return JSONResponse(
            status_code=500,
            content={"valid": False, "reason": "network", "detail": str(exc)[:200]},
        )

    if r.status_code == 200:
        return {"valid": True}

    if r.status_code == 429:
        return JSONResponse(
            status_code=429,
            content={"valid": False, "reason": "rate_limited"},
        )

    if r.status_code in (400, 401, 403):
        # Google answers 400 with body containing "API_KEY_INVALID" for bad keys.
        body_text = (r.text or "").lower()
        if "api_key_invalid" in body_text or "api key not valid" in body_text:
            return JSONResponse(
                status_code=401,
                content={"valid": False, "reason": "invalid_key"},
            )
        return JSONResponse(
            status_code=401,
            content={"valid": False, "reason": "rejected", "detail": r.text[:200]},
        )

    return JSONResponse(
        status_code=500,
        content={"valid": False, "reason": "upstream_error", "status": r.status_code},
    )


@app.post("/api/upload")
@limiter.limit("10/minute")
async def upload(request: Request, file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in storage.ALLOWED_EXTS:
        raise HTTPException(
            status_code=400,
            detail=f"unsupported file type: {ext or '<none>'} (allowed: {sorted(storage.ALLOWED_EXTS)})",
        )

    contents = await file.read()
    if len(contents) > storage.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"file too large (max {storage.MAX_FILE_SIZE} bytes)")

    run_id = storage.new_run_id()
    target = storage.input_path(run_id, file.filename or f"input{ext}")
    target.write_bytes(contents)

    return {
        "run_id": run_id,
        "filename": target.name,
        "size_bytes": len(contents),
    }


@app.post("/api/run/{run_id}")
@limiter.limit("5/minute")
async def start_run(run_id: str, body: RunRequest, request: Request):
    input_file = storage.find_input_file(run_id)
    if input_file is None:
        raise HTTPException(status_code=404, detail="run_id not found or no input file uploaded")

    output_path = str(storage.report_path(run_id))
    try:
        await runner.submit(run_id, str(input_file), body.api_key, output_path)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    return {"run_id": run_id, "status": "queued", "queue_size": runner.queue_size}


@app.get("/api/state/{run_id}")
async def get_state(run_id: str):
    """Return current run status without attaching to the SSE stream.
    Used by the frontend to recover state after a page refresh."""
    try:
        state = runner.get_state(run_id)
    except RunNotFound:
        raise HTTPException(status_code=404, detail="run not found")
    return {
        "run_id": run_id,
        "status": state.status,
        "error": state.error,
        "queue_position": runner.get_queue_position(run_id),
    }


@app.get("/api/events/{run_id}")
async def events(run_id: str):
    try:
        emitter = runner.get_emitter(run_id)
    except RunNotFound:
        raise HTTPException(status_code=404, detail="run not found")

    async def stream():
        async for chunk in emitter.stream():
            yield chunk

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.get("/api/report/{run_id}")
async def report(run_id: str):
    p = storage.report_path(run_id)
    if not p.exists():
        raise HTTPException(status_code=404, detail="report not ready")
    return FileResponse(str(p), media_type="text/html")


@app.post("/api/cancel/{run_id}")
async def cancel(run_id: str):
    if not runner.set_cancel(run_id):
        raise HTTPException(status_code=404, detail="run not found")
    return {"run_id": run_id, "cancel_requested": True}
