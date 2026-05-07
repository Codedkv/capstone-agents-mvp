"""
Filesystem layout for per-run artifacts.

    <project_root>/runs/{run_id}/<original-filename>   # uploaded input
    <project_root>/runs/{run_id}/report.html           # generated HTML report

The runs directory is anchored to the project root via core.paths so the
backend can be launched from any CWD (uvicorn from a subdir, systemd
WorkingDirectory mismatch, etc.) without losing track of run artifacts.
"""

import os
import uuid
from pathlib import Path

from core.paths import RUNS_DIR

RUNS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTS = {".csv", ".xlsx", ".xls", ".json"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def new_run_id() -> str:
    return uuid.uuid4().hex[:12]


def run_dir(run_id: str) -> Path:
    p = RUNS_DIR / run_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def input_path(run_id: str, filename: str) -> Path:
    # Strip any directory component from the uploaded filename to prevent
    # path traversal — `os.path.basename` is enough because the filename
    # comes from a multipart upload header, not from a URL.
    safe = os.path.basename(filename) or "input"
    return run_dir(run_id) / safe


def report_path(run_id: str) -> Path:
    return run_dir(run_id) / "report.html"


def find_input_file(run_id: str) -> Path | None:
    rd = RUNS_DIR / run_id
    if not rd.exists():
        return None
    for p in rd.iterdir():
        if p.suffix.lower() in ALLOWED_EXTS:
            return p
    return None
