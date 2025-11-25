import statistics
from typing import List, Dict, Any, Literal

def _ensure_dict(obj):
    """
    Helper: convert MapComposite/generativeai objects to plain dict recursively.
    Also handles lists of such objects.
    """
    # If it's already a dict, copy it
    if isinstance(obj, dict):
        return {k: _ensure_dict(v) for k, v in obj.items()}
    # If it's a list, process each element
    if isinstance(obj, list):
        return [_ensure_dict(elem) for elem in obj]
    # Gemini sometimes returns MapComposite
    if hasattr(obj, "items"):
        return {k: _ensure_dict(v) for k, v in obj.items()}
    # If it's not a dict/list, just return it
    return obj

def detect_anomalies(
    data: List[Dict[str, Any]], 
    method: Literal["iqr", "zscore"] = "iqr", 
    threshold: float = 1.5
) -> Dict[str, Any]:
    """
    Detect anomalies in business data using IQR or Z-score methods.
    
    Args:
        data: List of dictionaries, each dict represents a row of business metrics (must contain 'revenue' field)
        method: Detection method - 'iqr' (Interquartile Range) or 'zscore' (Z-score)
        threshold: Sensitivity for detection (default 1.5 for IQR, 3.0 recommended for zscore)
    
    Returns:
        Dictionary with keys:
        - anomalies: List of rows identified as anomalies
        - total: Number of anomalies detected
        - method: Method used for detection
    """
    # Ensure input data is 100% plain dict/list
    data = _ensure_dict(data)
    if not data or not isinstance(data, list) or len(data) == 0:
        return {"anomalies": [], "total": 0, "method": method}
    
    # Extract revenue values
    values = [float(row.get("revenue", 0)) for row in data if isinstance(row, dict) and "revenue" in row]
    
    if len(values) < 2:
        return {"anomalies": [], "total": 0, "method": method}
    
    anomalies = []
    
    if method == "iqr":
        q1 = statistics.quantiles(values, n=4)[0]
        q3 = statistics.quantiles(values, n=4)[2]
        iqr = q3 - q1
        lower = q1 - threshold * iqr
        upper = q3 + threshold * iqr
        for row in data:
            v = float(row.get("revenue", 0))
            if v < lower or v > upper:
                anomalies.append(row)
    
    elif method == "zscore":
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        if stdev > 0:
            for row in data:
                v = float(row.get("revenue", 0))
                z = (v - mean) / stdev
                if abs(z) > threshold:
                    anomalies.append(row)
    
    return {
        "anomalies": anomalies, 
        "total": len(anomalies), 
        "method": method
    }
