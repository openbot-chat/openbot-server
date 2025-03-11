from uuid import UUID
from typing import Optional, Dict, Any
from fastapi import Depends
from repositories.sqlalchemy.prompt_repository import PromptRepository
from api.dependencies.repository import make_repository
from models.prompt import *
from schemas.pagination import CursorParams, CursorPage



class PromptService:
    def __init__(self, repository: PromptRepository = Depends(make_repository(PromptRepository))):
        self.repository = repository
    
    async def create(self, in_schema: CreatePromptSchema) -> PromptSchema:
        return await self.repository.create(in_schema)

    async def get_by_id(self, id: UUID) -> Optional[PromptSchema]:
        return await self.repository.get_by_id(id)

    async def update_by_id(self, id: UUID, data: UpdatePromptSchema) -> PromptSchema:
        return await self.repository.update_by_id(id, data)

    async def delete_by_id(self, id: UUID) -> Optional[PromptSchema]:
        return await self.repository.delete_by_id(id)

    async def paginate(self, filter: Dict[str, Any], params: Optional[CursorParams]) -> CursorPage[PromptSchema]:
        return await self.repository.paginate1(filter, params=params)