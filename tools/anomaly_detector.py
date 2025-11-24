import statistics

def detect_anomalies(data, method="iqr", threshold=1.5):
    """
    Detect anomalies in business data using IQR or Z-score methods.
    Arguments:
        data: list of dicts, each dict = row of metrics
        method: "iqr" or "zscore"
        threshold: sensitivity for detection
    Returns:
        dict: { "anomalies": [rows], "total": N, "method": str }
    """
    if not data or not isinstance(data, list) or len(data) == 0:
        return {"anomalies": [], "total": 0, "method": method}
    # Example: run only on 'revenue' column
    values = [float(row.get("revenue", 0)) for row in data if "revenue" in row]
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
    if method == "zscore":
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        for row in data:
            v = float(row.get("revenue", 0))
            z = (v - mean) / stdev if stdev else 0
            if abs(z) > threshold:
                anomalies.append(row)
    return {"anomalies": anomalies, "total": len(anomalies), "method": method}
