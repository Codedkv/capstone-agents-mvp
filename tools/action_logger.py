import json
from datetime import datetime

from core.paths import DEFAULT_AGENT_LOG, LOGS_DIR

def _convert_to_serializable(obj):
    """
    Recursively convert protobuf MapComposite and other non-serializable objects to Python dict/list.
    """
    # Handle MapComposite (protobuf map)
    if hasattr(obj, '__class__') and 'MapComposite' in obj.__class__.__name__:
        return {k: _convert_to_serializable(v) for k, v in obj.items()}
    
    # Handle dict
    if isinstance(obj, dict):
        return {k: _convert_to_serializable(v) for k, v in obj.items()}
    
    # Handle list/tuple
    if isinstance(obj, (list, tuple)):
        return [_convert_to_serializable(item) for item in obj]
    
    # Handle primitive types
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    
    # Fallback: convert to string
    return str(obj)

def log_agent_action(agent_name, action, details=None):
    """
    Log agent action to logs/agent_actions.log with timestamp and metadata.
    Handles protobuf MapComposite and other non-serializable objects.
    
    Arguments:
        agent_name: str (name of the agent)
        action: str (description of the action)
        details: any (optional metadata — will be converted to JSON-safe format)
    
    Returns:
        dict: Confirmation of logged action
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = DEFAULT_AGENT_LOG

    safe_details = _convert_to_serializable(details) if details is not None else None

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent_name,
        "action": action,
        "details": safe_details,
    }

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return {
        "status": "success",
        "message": f"Action logged for {agent_name}",
        "log_file": str(log_file),
    }
