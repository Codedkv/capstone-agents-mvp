import pandas as pd
import json
import os

def search_trends(data, config_path="config/analysis_settings.json"):
    """
    Identify simple trends (e.g., increasing/decreasing values over time).
    
    Arguments:
        data: list[dict] OR str (filepath)
        config_path: str
    """
    try:
        # 1. Handle data input
        if isinstance(data, str):
            if not os.path.exists(data):
                return {"error": f"File not found: {data}"}
            
            ext = os.path.splitext(data)[-1].lower()
            if ext == '.csv':
                df = pd.read_csv(data)
            elif ext in ['.xls', '.xlsx']:
                df = pd.read_excel(data)
            else:
                return {"error": "Unsupported file format for trend search"}
        else:
            df = pd.DataFrame(data)

        if df.empty:
            return {"error": "Dataset is empty"}
            
        # 2. Load config to find date column
        with open(config_path, "r") as f:
            config = json.load(f)
        
        # Try to guess date column or use config
        date_col = "date" # Default
        # If specifically defined in config, use it (optional logic)
        
        if date_col not in df.columns:
             return {"status": "skipped", "reason": "No 'date' column found for trend analysis"}

        # 3. Trend Logic
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.sort_values(by=date_col)
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        trends = {}
        
        for col in numeric_cols:
            if len(df) < 2:
                continue
                
            first_val = df[col].iloc[0]
            last_val = df[col].iloc[-1]
            change_pct = ((last_val - first_val) / first_val) * 100 if first_val != 0 else 0
            
            trend_direction = "stable"
            if change_pct > 5: trend_direction = "increasing"
            if change_pct < -5: trend_direction = "decreasing"
            
            trends[col] = {
                "direction": trend_direction,
                "change_percent": round(change_pct, 2),
                "start_val": float(first_val),
                "end_val": float(last_val)
            }

        return {
            "status": "success",
            "trends": trends
        }

    except Exception as e:
        return {"error": str(e)}
