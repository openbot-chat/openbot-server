from typing import Type, Dict, Any, Optional

from sqlalchemy import desc
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.future import select

from repositories.sqlalchemy.prompt import Prompt
from repositories.sqlalchemy.base_repository import BaseRepository
from schemas.pagination import CursorParams, CursorPage

from models.prompt import (
    CreatePromptSchema,
    UpdatePromptSchema,
    PromptSchema,
)



class PromptRepository(BaseRepository[
    CreatePromptSchema,
    UpdatePromptSchema,
    PromptSchema,
    Prompt,
]):
    @property
    def _table(self) -> Type[Prompt]:
        return Prompt

    @property
    def _schema(self) -> Type[PromptSchema]:
        return PromptSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(Prompt.created_at)
    
    async def paginate1(self, filter: Dict[str, Any], params: Optional[CursorParams] = None) -> CursorPage[PromptSchema]:
        query = select(self._table).order_by(self._order_by)

        if 'q' in filter:
            query = query.where(
                Prompt.name.ilike(f"%{filter['q']}%"),
            )

        if 'org_id' in filter:
            query = query.where(
                Prompt.org_id == filter['org_id'],
            )

        return await super().paginate(query, params)