import os
import json
from datetime import datetime
from .base_tool import BaseTool

class ActionLoggerTool(BaseTool):
    def __init__(self):
        super().__init__("log_agent_action", "Structured JSONL action logger")

    async def execute(self, agent_name, action, details=None, level="INFO"):
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "agent": agent_name,
                "action": action,
                "details": details if details else {},
                "level": level
            }

            log_dir = "./logs"
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "agent_actions.jsonl")

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

            return type("Result", (), {
                "success": True,
                "data": {
                    "logged": True,
                    "log_file": log_file,
                    "entry": log_entry
                }
            })()

        except Exception as e:
            return type("Result", (), {
                "success": False,
                "data": None,
                "error": f"Logging failed: {e}"
            })()
