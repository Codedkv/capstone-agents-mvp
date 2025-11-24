class BaseTool:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description

    async def execute(self, *args, **kwargs):
        raise NotImplementedError("Must be implemented in subclass")
