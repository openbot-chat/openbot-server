from typing import Type, Optional, Dict, Any

from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc
from sqlalchemy.future import select
from repositories.sqlalchemy.datasource import Datasource
from repositories.sqlalchemy.base_repository import BaseRepository
from schemas.pagination import CursorParams, CursorPage

from models.datasource import (
    CreateDatasourceSchema,
    UpdateDatasourceSchema,
    DatasourceSchema,
)

class DatasourceRepository(BaseRepository[
    CreateDatasourceSchema,
    UpdateDatasourceSchema,
    DatasourceSchema,
    Datasource,
]):
    @property
    def _table(self) -> Type[Datasource]:
        return Datasource

    @property
    def _schema(self) -> Type[DatasourceSchema]:
        return DatasourceSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(Datasource.created_at)
  
    # 要去掉的
    async def query_one(
        self,
        filter: Dict[str, Any],
    ) -> Optional[DatasourceSchema]:
        query = select(self._table).order_by(self._table.created_at.desc())
        if "datasource_id" in filter:
            query = query.where(
                Datasource.id == filter['datasource_id']
            )

        if 'datastore_id' in filter:
            query = query.where(
                Datasource.datastore_id == filter['datastore_id']
            )
        entry = (await self._db_session.execute(query)).scalar_one_or_none()
        if not entry:
            return None
        
        return self._schema.from_orm(entry)

    async def paginate1(
        self,
        filter: Dict[str, Any],
        params: Optional[CursorParams] = None, 
    ) -> CursorPage[DatasourceSchema]:
        query = select(self._table).order_by(self._table.created_at.desc())
        if 'datastore_id' in filter:
            query = query.where(
                Datasource.datastore_id == filter['datastore_id'],
            )

        if 'status' in filter:
            query = query.where(
                Datasource.status.in_(filter['status']),
            )

        return await super().paginate(query, params)

    async def count1(
        self,
        filter: Dict[str, Any],
    ) -> int:
        query = select(self._table)
        if 'datastore_id' in filter:
            query = query.where(
                Datasource.datastore_id == filter['datastore_id'],
            )

        if 'status' in filter:
            query = query.where(
                Datasource.status.in_(filter['status']),
            )

        return await super().count(query)