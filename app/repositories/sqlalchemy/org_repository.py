from typing import Type, Optional, Dict, Any

from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc
from sqlalchemy.future import select

from repositories.sqlalchemy.org import Org, OrgMember
from repositories.sqlalchemy.base_repository import BaseRepository
from schemas.pagination import CursorParams, CursorPage

from models.org import (
    CreateOrgSchema,
    UpdateOrgSchema,
    OrgSchema,
)

class OrgRepository(BaseRepository[
    CreateOrgSchema,
    UpdateOrgSchema,
    OrgSchema,
    Org,
]):
    @property
    def _table(self) -> Type[Org]:
        return Org

    @property
    def _schema(self) -> Type[OrgSchema]:
        return OrgSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(Org.created_at)

    async def query(self, filter: Dict[str, Any], params: Optional[CursorParams] = None) -> CursorPage[OrgSchema]:
        query = select(self._table).join(OrgMember).order_by(self._order_by)

        if 'user_id' in filter:
            query = query.where(
                OrgMember.user_id == filter['user_id'],
            )

        return await super().paginate(query, params)