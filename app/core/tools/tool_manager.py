from typing import Dict, Any, Type
from models.tool import *

from .openapi import OpenApiTool, OpenApiExecutor

class ToolRunner(BaseModel):
    tool_info: ToolSchema

    async def run(self, inputs: Any):
        ...


class OpenApiToolRunner(ToolRunner):
    async def run(self, inputs: Any):
        spec_text = str(self.tool_info.options.get("spec"))

        executor = OpenApiExecutor(spec=spec_text)
        return await executor.run(inputs)



tool_cls: Dict[str, Type[ToolRunner]] = {
    "openapi": OpenApiToolRunner
}



class ToolManager:
    async def run(self, tool_info: ToolSchema, inputs: Dict[str, Any]):
        cls = tool_cls.get(tool_info.type)
        if not cls:
            raise Exception(f"tool type {tool_info.type} not found")
        
        runner: ToolRunner = cls(tool_info=tool_info)

        return await runner.run(inputs)