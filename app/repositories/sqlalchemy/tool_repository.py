from typing import Type, Optional, Any, Dict
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc
from .tool import Tool
from repositories.sqlalchemy.base_repository import BaseRepository
from sqlalchemy.future import select
from sqlalchemy.sql import Select
from schemas.pagination import CursorParams, CursorPage


from models.tool import (
    CreateToolSchema,
    UpdateToolSchema,
    ToolSchema,
    ToolFilter,
)

class ToolRepository(BaseRepository[
    CreateToolSchema,
    UpdateToolSchema,
    ToolSchema,
    Tool,
]):
    @property
    def _table(self) -> Type[Tool]:
        return Tool

    @property
    def _schema(self) -> Type[ToolSchema]:
        return ToolSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(Tool.created_at)
    
    async def paginate1(self, filter: ToolFilter, params: Optional[CursorParams] = None) -> CursorPage[ToolSchema]:
        query = select(self._table).order_by(self._order_by)

        if filter.org_id is not None:
            query = query.where(
                Tool.org_id == filter.org_id,
            )

        if filter.toolkit_id is not None:
            query = query.where(
                Tool.toolkit_id == filter.toolkit_id,
            )
        else:
            query = query.where(
                Tool.toolkit_id.is_(None),
            )

        return await super().paginate(query, params)