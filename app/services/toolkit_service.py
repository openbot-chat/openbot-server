from uuid import UUID
from typing import Optional, List
from fastapi import Depends
from repositories.sqlalchemy.toolkit_repository import ToolkitRepository
from api.dependencies.repository import make_repository
from models.toolkit import *
from schemas.pagination import CursorParams, CursorPage



class ToolkitService:
    def __init__(self, repository: ToolkitRepository = Depends(make_repository(ToolkitRepository))):
        self.repository = repository
  
    async def create(self, in_schema: CreateToolkitSchema) -> ToolkitSchema:
        return await self.repository.create(in_schema)

    async def get_by_id(self, id: UUID) -> Optional[ToolkitSchema]:
        return await self.repository.get_by_id(id)

    async def get_by_ids(self, ids: List[UUID]) -> List[ToolSchema]:
        return await self.get_by_ids(ids)

    async def update_by_id(self, id: UUID, data: UpdateToolkitSchema) -> ToolkitSchema:
        return await self.repository.update_by_id(id, data)

    async def delete_by_id(self, id: UUID) -> ToolkitSchema:
        return await self.repository.delete_by_id(id)

    async def query(self, filter: Dict[str, Any], params: CursorParams) -> CursorPage[ToolkitSchema]:
        return await self.repository.query(filter, params=params)