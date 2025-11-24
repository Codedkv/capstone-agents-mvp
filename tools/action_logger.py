import json
import os

def log_agent_action(agent_name, action, details=None, log_path="logs/agent_actions.jsonl"):
    """
    Log an agent's action to a local JSONL file.
    Arguments:
        agent_name: str — name of the agent
        action: str — action performed
        details: dict/str — extra info (optional)
        log_path: str — where to store logs (default: logs/agent_actions.jsonl)
    Returns:
        bool: True on success
    """
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    entry = {
        "agent": agent_name,
        "action": action,
        "details": details,
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return True
