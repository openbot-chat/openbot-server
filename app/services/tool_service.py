from uuid import UUID
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from repositories.sqlalchemy.tool_repository import ToolRepository
from api.dependencies.repository import make_repository
from api.dependencies.tool_manager import get_tool_manager
from models.tool import *
from schemas.pagination import CursorParams, CursorPage
from core.tools.tool_manager import ToolManager


class ToolService:
    def __init__(
        self, 
        repository: ToolRepository = Depends(make_repository(ToolRepository)),
        tool_manager: ToolManager = Depends(get_tool_manager),
    ):
        self.repository = repository
        self.tool_manager = tool_manager
 
    async def create(self, in_schema: CreateToolSchema) -> ToolSchema:
        return await self.repository.create(in_schema)

    async def get_by_id(self, id: UUID) -> Optional[ToolSchema]:
        return await self.repository.get_by_id(id)

    async def get_by_ids(self, ids: List[UUID]) -> List[ToolSchema]:
        return await self.get_by_ids(ids)

    async def update_by_id(self, id: UUID, data: UpdateToolSchema) -> ToolSchema:
        return await self.repository.update_by_id(id, data)

    async def delete_by_id(self, id: UUID) -> ToolSchema:
        return await self.repository.delete_by_id(id)

    async def paginate(self, filter: ToolFilter, params: CursorParams) -> CursorPage[ToolSchema]:
        return await self.repository.paginate1(filter, params=params)
    

    async def run(self, tool_id: UUID, req: ToolRunRequest) -> ToolRunResponse:
        tool = await self.get_by_id(tool_id)
        if not tool:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")

        outputs = await self.tool_manager.run(tool, req.inputs)
        
        return ToolRunResponse(
            outputs=outputs
        )