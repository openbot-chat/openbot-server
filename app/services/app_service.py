from uuid import UUID
from typing import Optional, List
from fastapi import Depends
from repositories.sqlalchemy.app_repository import AppRepository
from api.dependencies.repository import make_repository
from models.wf_app import *
from schemas.pagination import CursorParams, CursorPage


class AppService:
    def __init__(
        self, 
        repository: AppRepository = Depends(make_repository(AppRepository)),
    ):
        self.repository = repository
 
    async def create(self, in_schema: CreateAppSchema) -> AppSchema:
        return await self.repository.create(in_schema)

    async def get_by_id(self, id: UUID) -> Optional[AppSchema]:
        return await self.repository.get_by_id(id)

    async def get_by_ids(self, ids: List[UUID]) -> List[AppSchema]:
        return await self.get_by_ids(ids)

    async def update_by_id(self, id: UUID, data: UpdateAppSchema) -> AppSchema:
        return await self.repository.update_by_id(id, data)

    async def delete_by_id(self, id: UUID) -> AppSchema:
        return await self.repository.delete_by_id(id)

    async def paginate(self, filter: AppFilter, params: CursorParams) -> CursorPage[AppSchema]:
        return await self.repository.query(filter, params=params)