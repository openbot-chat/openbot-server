from typing import Type, List, Optional, Dict, Any

from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import delete, desc
from sqlalchemy.future import select
from sqlalchemy.orm import InstrumentedAttribute, selectinload
from repositories.sqlalchemy.org import OrgMember
from repositories.sqlalchemy.base_repository import BaseRepository
from schemas.pagination import CursorParams, CursorPage
from .user import User
from uuid import UUID

from models.org_member import (
    CreateOrgMemberSchema,
    UpdateOrgMemberSchema,
    OrgMemberSchema,
)




class OrgMemberRepository(BaseRepository[
    CreateOrgMemberSchema,
    UpdateOrgMemberSchema,
    OrgMemberSchema,
    OrgMember,
]):
    @property
    def _table(self) -> Type[OrgMember]:
        return OrgMember

    @property
    def _schema(self) -> Type[OrgMemberSchema]:
        return OrgMemberSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(OrgMember.created_at)

    async def remove_members(self, org_id: UUID, ids: List[str]) -> List[OrgMemberSchema]:
        query = select(OrgMember).where(
          OrgMember.org_id == org_id,
          OrgMember.id.in_(ids),
        )

        result = await self._db_session.scalars(
            delete(OrgMember, query).returning(OrgMember)
        )

        await self._db_session.flush()
        return list(result)
  
    async def get_member(self, org_id: UUID, user_id: UUID) -> Optional[OrgMemberSchema]:
        result = await self._db_session.execute(
            select(OrgMember).filter(
              OrgMember.org_id == org_id, 
              OrgMember.user_id == user_id,
            )
        )

        entry = result.scalar_one_or_none()
        if not entry:
            return None
        return self._schema.from_orm(entry)

    async def list(
        self,
        filter: Dict[str, Any] = {},
        params: Optional[CursorParams] = None, 
    ) -> CursorPage[OrgMemberSchema]:
        query = select(self._table).order_by(self._table.created_at.desc()).options(
            selectinload(self._table.user)
            # .load_only(User.id, User.name, User.avatar),
        )

        if 'org_id' in filter:
            query = query.where(
                OrgMember.org_id == filter['org_id'],
            )

        return await super().paginate(query, params)