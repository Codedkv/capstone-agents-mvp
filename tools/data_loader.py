import csv
from .base_tool import BaseTool

class DataLoaderTool(BaseTool):
    def __init__(self):
        super().__init__("load_csv_data", "Load and validate CSV files")

    async def execute(self, filepath, validate=True, max_rows=10000):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = [row for idx, row in enumerate(reader) if idx < max_rows]
            if validate:
                required_cols = {'date', 'revenue', 'costs', 'customers'}
                if not required_cols.issubset(set(data[0].keys())):
                    return type("Result", (), {
                        "success": False,
                        "data": None,
                        "error": "Invalid CSV format: missing required columns"
                    })()
            return type("Result", (), {
                "success": True,
                "data": data,
                "row_count": len(data),
                "columns": list(data[0].keys())
            })()
        except FileNotFoundError:
            return type("Result", (), {
                "success": False,
                "data": None,
                "error": "File not found"
            })()
        except Exception as e:
            return type("Result", (), {
                "success": False,
                "data": None,
                "error": f"Data loading failed: {e}"
            })()

async def load_csv_data(filepath, validate=True, max_rows=10000):
    """
    Async wrapper for loading and validating CSV business metrics.
    Returns result object with success/data/error etc.
    """
    tool = DataLoaderTool()
    return await tool.execute(filepath, validate=validate, max_rows=max_rows)

def validate_schema(data, required_cols=None):
    """
    Validate if dataset contains all required columns.
    Used by DataLoader and agents.
    """
    required = required_cols or {'date', 'revenue', 'costs', 'customers'}
    if not data or not isinstance(data, list) or len(data) == 0:
        return False
    if isinstance(data[0], dict):
        return required.issubset(set(data[0].keys()))
    return False
