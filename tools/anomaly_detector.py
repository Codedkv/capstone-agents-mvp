import statistics
from .base_tool import BaseTool

class AnomalyDetectorTool(BaseTool):
    def __init__(self):
        super().__init__("detect_anomalies", "Statistical anomaly detection (IQR, Z-score, Threshold)")

    async def execute(self, data, method="iqr", threshold=1.5):
        try:
            if not isinstance(data, list) or len(data) < 3:
                return type("Result", (), {
                    "success": False, "data": None,
                    "error": "Insufficient data"
                })()

            anomalies = []
            if method == "iqr":
                sorted_data = sorted(data)
                q1 = sorted_data[len(sorted_data) // 4]
                q3 = sorted_data[3 * len(sorted_data) // 4]
                iqr = q3 - q1
                lower = q1 - threshold * iqr
                upper = q3 + threshold * iqr
                anomalies = [v for v in data if v < lower or v > upper]

            elif method == "zscore":
                mean = statistics.mean(data)
                stdev = statistics.stdev(data)
                anomalies = [v for v in data if stdev > 0 and abs((v - mean) / stdev) > (threshold if threshold else 3)]

            elif method == "threshold":
                anomalies = [v for v in data if abs(v) > threshold]

            else:
                return type("Result", (), {
                    "success": False, "data": None,
                    "error": f"Unknown method: {method}"
                })()

            return type("Result", (), {
                "success": True,
                "data": {
                    "anomalies": anomalies,
                    "count": len(anomalies),
                    "method": method
                }
            })()
        except Exception as e:
            return type("Result", (), {
                "success": False, "data": None,
                "error": f"Detection failed: {e}"
            })()
