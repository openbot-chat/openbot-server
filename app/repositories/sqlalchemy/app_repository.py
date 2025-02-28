from typing import Type, Optional, Any, Dict
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc
from .app import App
from repositories.sqlalchemy.base_repository import BaseRepository
from sqlalchemy.future import select
from schemas.pagination import CursorParams, CursorPage

from models.wf_app import (
    CreateAppSchema,
    UpdateAppSchema,
    AppSchema,
    AppFilter,
)

class AppRepository(BaseRepository[
    CreateAppSchema,
    UpdateAppSchema,
    AppSchema,
    App,
]):
    @property
    def _table(self) -> Type[App]:
        return App

    @property
    def _schema(self) -> Type[AppSchema]:
        return AppSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(App.created_at)
    
    async def query(self, filter: AppFilter, params: Optional[CursorParams] = None) -> CursorPage[AppSchema]:
        query = select(self._table).order_by(self._order_by)

        if filter.org_id is not None:
            query = query.where(
                App.org_id == filter.org_id,
            )

        if filter.name is not None:
            query = query.where(
                App.name.ilike(f"%{filter.name}%"),
            )
        
        return await super().paginate(query, params)