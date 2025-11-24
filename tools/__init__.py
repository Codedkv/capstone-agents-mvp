from .base_tool import BaseTool
from .data_loader import DataLoaderTool
from .anomaly_detector import AnomalyDetectorTool
from .market_trends import MarketTrendsTool
from .report_generator import ReportGeneratorTool
from .action_logger import ActionLoggerTool

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, tool):
        self.tools[tool.name] = tool

    def get_tool(self, name):
        return self.tools.get(name)

    def list_tool_names(self):
        return list(self.tools.keys())
