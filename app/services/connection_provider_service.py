from uuid import UUID
from typing import Optional
from fastapi import Depends
from repositories.sqlalchemy.connection_provider_repository import ConnectionProviderRepository
from api.dependencies.repository import make_repository
from models.connection_provider import *
from schemas.pagination import CursorParams
from schemas.pagination import CursorParams, CursorPage



class ConnectionProviderService:
    def __init__(
      self, 
      repository: ConnectionProviderRepository = Depends(make_repository(ConnectionProviderRepository)),
    ):
        self.repository = repository
  
    async def create(self, in_schema: CreateConnectionProviderSchema) -> ConnectionProviderSchema:
        return await self.repository.create(in_schema)

    # TODO 缓存
    async def get_by_id(self, id: UUID) -> Optional[ConnectionProviderSchema]:
        return await self.repository.get_by_id(id)

    async def get_by_identifier(self, identifier: str) -> Optional[ConnectionProviderSchema]:
        return await self.repository.get_by_identifier(identifier)

    async def update_by_id(self, id: UUID, data: UpdateConnectionProviderSchema) -> ConnectionProviderSchema:
      return await self.repository.update_by_id(id, data)

    async def delete_by_id(self, id: UUID) -> None:
        await self.repository.delete_by_id(id)
        return

    async def paginate(self, filter: ConnectionFilter, params: Optional[CursorParams] = None) -> CursorPage[ConnectionProviderSchema]:
        return await self.repository.query(filter, params=params)
  
    async def count(self) -> int:
        return await self.repository.count()