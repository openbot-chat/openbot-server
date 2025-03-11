from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import Depends
from repositories.sqlalchemy.org_repository import OrgRepository
from repositories.sqlalchemy.org_member_repository import OrgMemberRepository
from api.dependencies.repository import make_repository
from models.org import *
from models.org_member import *
from schemas.pagination import CursorParams, CursorPage

class OrgService:
    def __init__(
        self, 
        repository: OrgRepository = Depends(make_repository(OrgRepository)),
        org_member_repository: OrgMemberRepository = Depends(make_repository(OrgMemberRepository)),
    ):
        self.repository = repository
        self.org_member_repository = org_member_repository
  
    async def create(self, in_schema: CreateOrgSchema) -> OrgSchema:
        return await self.repository.create(in_schema)

    async def get_by_id(self, id: UUID) -> Optional[OrgSchema]:
        return await self.repository.get_by_id(id)

    async def get_by_ids(self, ids: List[UUID]) -> List[OrgSchema]:
        return await self.repository.get_by_ids(ids)

    async def update_by_id(self, id: UUID, data: UpdateOrgSchema) -> OrgSchema:
        return await self.repository.update_by_id(id, data)

    async def delete_by_id(self, id: UUID) -> OrgSchema:
        return await self.repository.delete_by_id(id)

    async def paginate(self, filter: Dict[str, Any] = {}, params: Optional[CursorParams] = None) -> CursorPage[OrgSchema]:
        return await self.repository.query(filter, params=params)

    async def query_one(self, filter: Dict[str, Any] = {}) -> Optional[OrgSchema]:
        return await self.repository.query_one(**filter)

    async def add_members(self, in_schema: List[CreateOrgMemberSchema]) -> List[OrgMemberSchema]:
        return await self.org_member_repository.create_many(in_schema)

    async def remove_members(self, org_id: UUID, ids: List[str]) -> List[OrgMemberSchema]:
        return await self.org_member_repository.remove_members(org_id, ids)
  
    async def get_member(self, org_id: UUID, user_id: UUID) -> Optional[OrgMemberSchema]:
        return await self.org_member_repository.get_member(org_id, user_id)

    async def list_members(self, org_id: UUID, filter: Dict[str, Any] = {}, params: Optional[CursorParams] = None) -> CursorPage[OrgMemberSchema]:
        new_fitler: Dict[str, Any] = {
            'org_id': org_id,
        }
        new_fitler.update(filter)

        return await self.org_member_repository.list(new_fitler, params=params)