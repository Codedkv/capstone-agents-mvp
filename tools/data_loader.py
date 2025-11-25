import os
import csv
import json
from typing import Dict, Any, List, Optional
import pandas as pd  # For Excel and DataFrame
from PyPDF2 import PdfReader  # For PDF text

def _ensure_dict(obj):
    """Recursively convert objects to plain dict/list."""
    if isinstance(obj, dict):
        return {k: _ensure_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_ensure_dict(elem) for elem in obj]
    if hasattr(obj, "items"):
        return {k: _ensure_dict(v) for k, v in obj.items()}
    return obj

def load_data(
    filepath: str,
    validate: bool = True,
    max_rows: int = 10000
) -> Dict[str, Any]:
    """
    Load and validate business data from CSV, JSON, XLSX, or PDF.

    Args:
        filepath: Path to data file.
        validate: Whether to validate required columns (for tabular data)
        max_rows: Max number of rows for large files

    Returns:
        status, message, data (list[dict] or str), columns, row_count
    """
    ext = os.path.splitext(filepath)[-1].lower()
    try:
        # CSV
        if ext == ".csv":
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = [row for idx, row in enumerate(reader) if idx < max_rows]
            data = _ensure_dict(data)
            columns = list(data[0].keys()) if data else []
        # JSON
        elif ext in [".json"]:
            with open(filepath, "r", encoding='utf-8') as f:
                data = json.load(f)
            # Accept both list[dict] and dicts (convert to list)
            if isinstance(data, dict):
                data = [data]
            data = _ensure_dict(data)
            columns = list(data[0].keys()) if data and isinstance(data[0], dict) else []
        # Excel (xlsx)
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(filepath, nrows=max_rows)
            data = df.to_dict(orient="records")
            data = _ensure_dict(data)
            columns = list(df.columns)
        # PDF (just raw text, for downstream NLP agents)
        elif ext == ".pdf":
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            # data as a single text field
            data = [{"text": text}]
            columns = ["text"]
        # Unknown/ext unsupported
        else:
            return {
                "status": "error",
                "message": f"Unsupported file type: {ext}",
                "data": [],
                "columns": [],
                "row_count": 0
            }

        # Validate for tabular formats only
        if validate and ext in [".csv", ".json", ".xlsx", ".xls"]:
            required_cols = {'date', 'revenue', 'costs', 'customers'}
            actual_cols = set(columns)
            if not required_cols.issubset(actual_cols):
                missing = required_cols - actual_cols
                return {
                    "status": "error",
                    "message": f"Missing required columns: {missing}",
                    "data": [],
                    "columns": columns,
                    "row_count": len(data)
                }

        return {
            "status": "success",
            "message": f"Data loaded successfully from {os.path.basename(filepath)}",
            "data": data,
            "columns": columns,
            "row_count": len(data)
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "message": f"File not found: {filepath}",
            "data": [],
            "columns": [],
            "row_count": 0
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Data loading failed: {str(e)}",
            "data": [],
            "columns": [],
            "row_count": 0
        }

def validate_schema(
    data: Optional[List[Dict[str, Any]]],
    required_cols: Optional[set] = None
) -> bool:
    """
    Validate that dataset contains required columns.
    """
    required = required_cols or {'date', 'revenue', 'costs', 'customers'}
    data = _ensure_dict(data)
    if not data or not isinstance(data, list) or len(data) == 0:
        return False
    if isinstance(data[0], dict):
        return required.issubset(set(data[0].keys()))
    return False
