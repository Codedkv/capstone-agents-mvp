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
