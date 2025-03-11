from typing import Type, Optional

from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc
from sqlalchemy.future import select
from sqlalchemy.sql import Select

from repositories.sqlalchemy.connection_provider import ConnectionProvider
from repositories.sqlalchemy.base_repository import BaseRepository

from models.connection_provider import (
    CreateConnectionProviderSchema,
    UpdateConnectionProviderSchema,
    ConnectionProviderSchema,
    ConnectionFilter,
)
from schemas.pagination import CursorParams, CursorPage



class ConnectionProviderRepository(BaseRepository[
    CreateConnectionProviderSchema,
    UpdateConnectionProviderSchema,
    ConnectionProviderSchema,
    ConnectionProvider,
]):
    @property
    def _table(self) -> Type[ConnectionProvider]:
        return ConnectionProvider

    @property
    def _schema(self) -> Type[ConnectionProviderSchema]:
        return ConnectionProviderSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(ConnectionProvider.created_at)

    async def get_by_identifier(self, identifier: str) -> Optional[ConnectionProviderSchema]:
        query = select(ConnectionProvider).where(
            ConnectionProvider.identifier == identifier,
        )
  
        entry = (await self._db_session.execute(query)).scalar_one_or_none()
        if not entry:
            return None
        return self._schema.from_orm(entry)


    async def query(self, filter: ConnectionFilter, params: Optional[CursorParams] = None) -> CursorPage[ConnectionProviderSchema]:
        query = select(self._table).order_by(self._order_by)

        if filter.app_id is not None:
            query = query.where(
                ConnectionProvider.app_id == filter.app_id,
            ) 
       
        return await super().paginate(query, params)