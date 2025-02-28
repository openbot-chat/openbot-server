from typing import List, Optional
from uuid import UUID
from fastapi import Depends
from repositories.sqlalchemy.account_repository import AccountRepository
from api.dependencies.repository import make_repository
from models.account import *
from schemas.pagination import CursorParams, CursorPage


class AccountService:
    def __init__(self, repository: AccountRepository = Depends(make_repository(AccountRepository))):
        self.repository = repository
  
    async def create(self, in_schema: CreateAccountSchema) -> AccountSchema:
        return await self.repository.create(in_schema)

    async def upsert(self, in_schema: UpdateAccountSchema) -> AccountSchema:
        return await self.repository.upsert_by_provider(in_schema)

    async def get_by_id(self, id: UUID) -> Optional[AccountSchema]:
        return await self.repository.get_by_id(id)

    async def update_by_id(self, id: UUID, data: UpdateAccountSchema) -> AccountSchema:
        return await self.repository.update_by_id(id, data)

    async def delete_by_id(self, id: UUID) -> AccountSchema:
        return await self.repository.delete_by_id(id)

    async def paginate(self, params: Optional[CursorParams] = None) -> CursorPage[AccountSchema]:
        return await self.repository.paginate(params=params)