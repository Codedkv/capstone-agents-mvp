import statistics
import json
from typing import List, Dict, Any

def _ensure_dict(obj):
    """Convert composite/generative objects to plain dict recursively."""
    if isinstance(obj, dict):
        return {k: _ensure_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_ensure_dict(elem) for elem in obj]
    if hasattr(obj, "items"):
        return {k: _ensure_dict(v) for k, v in obj.items()}
    return obj

def load_config(config_path: str = "config/analysis_settings.json") -> Dict[str, Any]:
    """Load anomaly detection config from JSON file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def detect_anomalies(
    data: List[Dict[str, Any]],
    config_path: str = "config/analysis_settings.json"
) -> Dict[str, Any]:
    """
    Detect anomalies in business data using config-driven settings.
    Scans all anomaly_columns for outliers and aggregates results.
    """
    config = load_config(config_path)
    anomaly_columns = config.get("anomaly_columns", [])
    method = config.get("anomaly_method", "iqr")
    threshold = config.get("anomaly_threshold", 1.5)
    data = _ensure_dict(data)

    if not data or not isinstance(data, list) or len(data) == 0:
        return {"status": "success", "anomalies": [], "count": 0, "columns": anomaly_columns, "method": method}

    all_anomalies = []

    for col in anomaly_columns:
        # Extract numerical values for current column
        values = [float(row.get(col, 0)) for row in data if isinstance(row, dict) and col in row]
        if len(values) < 2:
            continue
        anomalies_col = []
        if method == "iqr":
            try:
                q1 = statistics.quantiles(values, n=4)[0]
                q3 = statistics.quantiles(values, n=4)[2]
            except IndexError:
                continue
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            for row in data:
                v = float(row.get(col, 0))
                if v < lower or v > upper:
                    anomalies_col.append(row)
        elif method == "zscore":
            mean = statistics.mean(values)
            stdev = statistics.stdev(values) if len(values) > 1 else 0
            if stdev > 0:
                for row in data:
                    v = float(row.get(col, 0))
                    z = (v - mean) / stdev
                    if abs(z) > threshold:
                        anomalies_col.append(row)
        # Collect results for this column
        all_anomalies.extend(anomalies_col)

    # Deduplicate anomalies (by id/hash if available, else full row)
    seen = set()
    unique_anomalies = []
    for row in all_anomalies:
        key = tuple(sorted(row.items()))
        if key not in seen:
            seen.add(key)
            unique_anomalies.append(row)

    return {
        "status": "success",
        "anomalies": unique_anomalies,
        "count": len(unique_anomalies),
        "columns": anomaly_columns,
        "method": method
    }
