from typing import List, Optional
from uuid import UUID
from fastapi import Depends
from repositories.sqlalchemy.user_repository import UserRepository
from api.dependencies.repository import make_repository
from models.user import *
from models.org import *
from schemas.pagination import CursorParams, CursorPage


class UserService:
    def __init__(self, repository: UserRepository = Depends(make_repository(UserRepository))):
        self.repository = repository
  
    async def create(self, in_schema: CreateUserSchema) -> UserSchema:
        return await self.repository.create(in_schema)

    async def get_by_id(self, id: UUID) -> Optional[UserSchema]:
        return await self.repository.get_by_id(id)

    async def get_by_provider_account_id(self, provider: str, account_id: str) -> UserSchema:
        return await self.repository.get_by_provider_account_id(provider, account_id)

    async def get_by_email(self, email: str) -> UserSchema:
        return await self.repository.get_by_email(email)

    async def get_by_ids(self, ids: List[UUID]) -> List[UserSchema]:
        return await self.repository.get_by_ids(ids)

    async def update_by_id(self, id: UUID, data: UpdateUserSchema) -> UserSchema:
        return await self.repository.update_by_id(id, data)

    async def delete_by_id(self, id: UUID) -> None:
        return await self.repository.delete_by_id(id)

    async def paginate(self, params: Optional[CursorParams] = None) -> CursorPage[UserSchema]:
        return await self.repository.paginate(params=params)

    async def list_orgs_by_user(self, user_id: UUID) -> List[OrgSchema]:
        return await self.repository.list_orgs_by_user(user_id)