import pandas as pd
import numpy as np
import json
import os

def detect_anomalies(data, config_path="config/analysis_settings.json"):
    """
    Detect anomalies in the dataset using IQR or Z-score methods.
    
    Arguments:
        data: list[dict] OR str (filepath to .csv/.xlsx)
        config_path: str (path to config)
        
    Returns:
        dict: Anomaly report
    """
    try:
        # 1. Handle data input (List vs Filepath)
        if isinstance(data, str):
            if not os.path.exists(data):
                return {"error": f"File not found: {data}"}
            
            ext = os.path.splitext(data)[-1].lower()
            if ext == '.csv':
                df = pd.read_csv(data)
            elif ext in ['.xls', '.xlsx']:
                df = pd.read_excel(data)
            elif ext == '.json':
                df = pd.read_json(data)
            else:
                return {"error": "Unsupported file format provided to detector"}
        else:
            # Assume it's a list of dicts
            df = pd.DataFrame(data)

        if df.empty:
            return {"error": "Dataset is empty"}

        # 2. Load Config
        with open(config_path, "r") as f:
            config = json.load(f)
            
        anomaly_cols = config.get("anomaly_columns", [])
        method = config.get("anomaly_method", "iqr")
        threshold = config.get("anomaly_threshold", 1.5)

        anomalies_summary = {}
        
        # 3. Detection Logic
        for col in anomaly_cols:
            if col not in df.columns:
                continue
                
            # Ensure numeric
            series = pd.to_numeric(df[col], errors='coerce').dropna()
            
            if method == "iqr":
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - (threshold * IQR)
                upper_bound = Q3 + (threshold * IQR)
                
                outliers = series[(series < lower_bound) | (series > upper_bound)]
                
            elif method == "zscore":
                mean = series.mean()
                std = series.std()
                z_scores = (series - mean) / std
                outliers = series[abs(z_scores) > threshold]
            
            else:
                return {"error": f"Unknown method: {method}"}

            if not outliers.empty:
                anomalies_summary[col] = {
                    "count": len(outliers),
                    "min_outlier": float(outliers.min()),
                    "max_outlier": float(outliers.max()),
                    "indices": outliers.index.tolist()[:10]  # Limit output
                }

        return {
            "status": "success",
            "method": method,
            "anomalies_detected": len(anomalies_summary) > 0,
            "summary": anomalies_summary
        }

    except Exception as e:
        return {"error": str(e)}
