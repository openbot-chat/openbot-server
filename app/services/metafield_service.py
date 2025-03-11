from typing import Optional, Dict, Any, List
from fastapi import Depends
from repositories.sqlalchemy.metafield_repository import MetafieldRepository
from api.dependencies.repository import make_repository
from schemas.pagination import CursorParams, CursorPage
from models.metafield import *



class MetafieldService:
    def __init__(
        self, 
        repository: MetafieldRepository = Depends(make_repository(MetafieldRepository)),
    ):
        self.repository = repository

    async def create(self, in_schema: CreateMetafieldSchema) -> MetafieldSchema:
        return await self.repository.create(in_schema)

    async def get_by_id(self, id: UUID) -> Optional[MetafieldSchema]:
        return await self.repository.get_by_id(id)

    async def update_by_id(self, id: UUID, data: UpdateMetafieldSchema) -> MetafieldSchema:
        return await self.repository.update_by_id(id, data)

    async def delete_by_id(self, id: UUID) -> MetafieldSchema:
        return await self.repository.delete_by_id(id)

    async def query(self, filter: MetafieldFilter, params: Optional[CursorParams] = None) -> CursorPage[MetafieldSchema]:
        return await self.repository.query(filter, params=params)
  
    async def count(self, filter: MetafieldFilter) -> int:
        return await self.repository.count_by_filter(filter)