from uuid import UUID
from fastapi import Depends
from typing import Optional, Dict, Any
from repositories.sqlalchemy.api_key_repository import ApiKeyRepository
from api.dependencies.repository import make_repository
from models.api_key import *
from schemas.pagination import CursorParams, CursorPage
from core.helper import generate_string


class ApiKeyService:
    def __init__(self, repository: ApiKeyRepository = Depends(make_repository(ApiKeyRepository))):
        self.repository = repository
    
    async def create(self, in_schema: CreateApiKeySchema) -> ApiKeySchema:
        in_schema.token = await self.generate_api_key('openbot-', 32)
        return await self.repository.create(in_schema)

    async def generate_api_key(self, prefix: str, n: int):
        while True:
            result = prefix + generate_string(n)
            api_exists = await self.repository.get_by_token(result)
            if api_exists is None:
                break
        return result


    async def get_by_id(self, id: UUID) -> Optional[ApiKeySchema]:
        return await self.repository.get_by_id(id)

    async def get_by_token(self, token: str) -> Optional[ApiKeySchema]:
        return await self.repository.get_by_token(token)

    async def update_by_id(self, id: UUID, data: UpdateApiKeySchema) -> ApiKeySchema:
        return await self.repository.update_by_id(id, data)

    async def delete_by_id(self, id: UUID):
        return await self.repository.delete_by_id(id)

    async def paginate(self, filter: Dict[str, Any], params: Optional[CursorParams]) -> CursorPage[ApiKeySchema]:
        return await self.repository.paginate1(filter, params=params)