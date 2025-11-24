from .base_tool import BaseTool

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, tool):
        self.tools[tool.name] = tool

    def get_tool(self, name):
        return self.tools.get(name)

    def list_tool_names(self):
        return list(self.tools.keys())
