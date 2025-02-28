from typing import Optional, Any
from asyncer import asyncify
from inspect import signature
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
)
from langchain.tools import Tool


async def _arun(
    self,
    *args: Any,
    run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    **kwargs: Any,
) -> Any:
    """Use the tool asynchronously."""
    if self.coroutine:
        new_argument_supported = signature(self.coroutine).parameters.get(
            "callbacks"
        )
        return (
            await self.coroutine(
                *args,
                callbacks=run_manager.get_child() if run_manager else None,
                **kwargs,
            )
            if new_argument_supported
            else await self.coroutine(*args, **kwargs)
        )
    
    return await asyncify(self._run)(*args, run_manager=run_manager, **kwargs)
    
Tool._arun = _arun
