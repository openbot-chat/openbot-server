from typing import Type, Optional

from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc, delete
from sqlalchemy.sql import Select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select
from repositories.sqlalchemy.metafield import Metafield
from repositories.sqlalchemy.base_repository import BaseRepository
from schemas.pagination import CursorParams, CursorPage

from models.metafield import (
    CreateMetafieldSchema,
    UpdateMetafieldSchema,
    MetafieldSchema,
    MetafieldFilter,
)

class MetafieldRepository(BaseRepository[
    CreateMetafieldSchema,
    UpdateMetafieldSchema,
    MetafieldSchema,
    Metafield,
]):
    @property
    def _table(self) -> Type[Metafield]:
        return Metafield

    @property
    def _schema(self) -> Type[MetafieldSchema]:
        return MetafieldSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(Metafield.created_at)

    def _fill_filter(self, query: Select, filter: MetafieldFilter):
        if filter.namespace:
            query = query.where(
                Metafield.namespace == filter.namespace,
            )

        if filter.key:
            query = query.where(
                Metafield.key == filter.key,
            )

        if filter.owner_type:
            query = query.where(
                Metafield.owner_type == filter.owner_type,
            )

        if filter.owner_id:
            query = query.where(
                Metafield.owner_id == filter.owner_id,
            )

        return query

    async def query(
        self,
        filter: MetafieldFilter,
        params: Optional[CursorParams] = None,
    ) -> CursorPage[MetafieldSchema]:
        query = select(Metafield).order_by(Metafield.created_at.desc())
        query = self._fill_filter(query, filter)

        return await super().paginate(query, params)

    async def count_by_filter(
        self,
        filter: MetafieldFilter,
    ) -> int:
        query = select(Metafield)
        query = self._fill_filter(query, filter)

        return await super().count(query)