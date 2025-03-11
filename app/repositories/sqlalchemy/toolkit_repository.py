from typing import Type, Optional, Any, Dict
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc
from .toolkit import Toolkit
from repositories.sqlalchemy.base_repository import BaseRepository
from sqlalchemy.future import select
from sqlalchemy.sql import Select
from schemas.pagination import CursorParams, CursorPage


from models.toolkit import (
    CreateToolkitSchema,
    UpdateToolkitSchema,
    ToolkitSchema,
)

class ToolkitRepository(BaseRepository[
    CreateToolkitSchema,
    UpdateToolkitSchema,
    ToolkitSchema,
    Toolkit,
]):
    @property
    def _table(self) -> Type[Toolkit]:
        return Toolkit

    @property
    def _schema(self) -> Type[ToolkitSchema]:
        return ToolkitSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(Toolkit.created_at)
    
    async def query(self, filter: Dict[str, Any], params: Optional[CursorParams] = None) -> CursorPage[ToolkitSchema]:
        query = select(self._table).order_by(self._order_by)

        if 'org_id' in filter:
            query = query.where(
                Toolkit.org_id == filter['org_id'],
            )

        return await super().paginate(query, params)