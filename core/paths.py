"""
Centralised filesystem layout — anchors all paths to the project root,
NOT the current working directory.

Why this exists
---------------
Tools and agents are imported into multiple entry points: `python main.py`
(CLI), `uvicorn backend.main:app` (HTTP), notebooks, tests. Each can be
launched from a different CWD. Hardcoding default paths as relative
strings ("config/analysis_settings.json") makes the pipeline silently
break the moment something runs from a subdirectory — exactly what
happened during the frontend integration when the dev server was started
from `frontend/` and the agent pipeline crashed with
`[Errno 2] No such file or directory: 'config/analysis_settings.json'`.

Rule: every default path that points inside the repo MUST come from this
module. User-supplied paths (uploaded files, etc.) are passed through
verbatim — they are absolute or already validated by the caller.
"""

from pathlib import Path

# core/paths.py is two levels deep:  <project_root>/core/paths.py
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

CONFIG_DIR: Path = PROJECT_ROOT / "config"
DATA_DIR: Path = PROJECT_ROOT / "data"
LOGS_DIR: Path = PROJECT_ROOT / "logs"
OUTPUT_DIR: Path = PROJECT_ROOT / "output"
RUNS_DIR: Path = PROJECT_ROOT / "runs"

DEFAULT_ANALYSIS_CONFIG: Path = CONFIG_DIR / "analysis_settings.json"
DEFAULT_REPORT_OUTPUT: Path = OUTPUT_DIR / "analysis_report.html"
DEFAULT_AGENT_LOG: Path = LOGS_DIR / "agent_actions.log"
DEFAULT_ENV_FILE: Path = PROJECT_ROOT / ".env"
DEFAULT_METRICS_FILE: Path = DATA_DIR / "shipments_data.xlsx"
