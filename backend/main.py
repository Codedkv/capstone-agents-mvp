"""
Outlier backend — FastAPI wrapper around the 5-agent pipeline.

Run locally:
    uvicorn backend.main:app --reload --port 8000

Endpoints
---------
    GET  /api/health              -> liveness + queue size
    POST /api/upload              -> multipart upload, returns {run_id, ...}
    POST /api/run/{run_id}        -> body: {api_key}, kicks off pipeline
    GET  /api/events/{run_id}     -> SSE stream of pipeline events
    GET  /api/report/{run_id}     -> HTML report (when pipeline done)
    POST /api/cancel/{run_id}     -> request cancellation (best-effort)
"""

import os
from contextlib import asynccontextmanager

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
