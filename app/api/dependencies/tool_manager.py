from core.tools.tool_manager import ToolManager


# Dependency
async def get_tool_manager() -> ToolManager:
    return ToolManager()