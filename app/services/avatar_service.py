from typing import List, Optional
from uuid import UUID
from fastapi import Depends
# from api.dependencies.repository import make_repository
from models import avatar as avatar_schemas
from schemas.pagination import CursorParams, CursorPage



class AvatarService:
    def __init__(self):
        ...

    async def create(self, in_schema: avatar_schemas.CreateAvatarSchema) -> avatar_schemas.AvatarSchema:
        ...

    async def upsert(self, in_schema: avatar_schemas.CreateAvatarSchema) -> avatar_schemas.AvatarSchema:
        ...

    async def get_by_id(self, id: UUID) -> avatar_schemas.AvatarSchema:
        ...

    async def get_by_ids(self, ids: List[UUID]) -> List[avatar_schemas.AvatarSchema]:
        ...

    async def update_by_id(self, id: UUID, data: avatar_schemas.UpdateAvatarSchema) -> avatar_schemas.AvatarSchema:
        ...

    async def delete_by_id(self, id: UUID) -> None:
        ...

    async def paginate(self, params: Optional[CursorParams]) -> CursorPage[avatar_schemas.AvatarSchema]:
        ...