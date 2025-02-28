from uuid import UUID
from typing import Optional
from fastapi import Depends
from repositories.sqlalchemy.credentials_repository import CredentialsRepository
from api.dependencies.repository import make_repository
from models.credentials import *
from schemas.pagination import CursorParams, CursorPage



class CredentialsService:
    def __init__(
        self, 
        repository: CredentialsRepository = Depends(make_repository(CredentialsRepository)),
    ):
        self.repository = repository
  
    async def create(self, in_schema: CreateCredentialsSchema) -> CredentialsSchema:
        return await self.repository.create(in_schema)

    # TODO 缓存
    async def get_by_id(self, id: UUID) -> Optional[CredentialsSchema]:
        return await self.repository.get_by_id(id)

    async def update_by_id(self, id: UUID, data: UpdateCredentialsSchema) -> CredentialsSchema:
        return await self.repository.update_by_id(id, data)

    async def delete_by_id(self, id: UUID) -> None:
        await self.repository.delete_by_id(id)
        return

    async def paginate(self, filter: Dict[str, Any], params: Optional[CursorParams] = None) -> CursorPage[CredentialsSchema]:
        return await self.repository.query(filter, params=params)
  
    async def count(self, filter: Dict[str, Any]) -> int:
        return await self.repository.count1(filter)