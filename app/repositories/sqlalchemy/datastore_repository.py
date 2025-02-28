from typing import Type, Optional, Dict, Any

from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc, distinct
from sqlalchemy.future import select
from sqlalchemy.sql import Select, func
from schemas.pagination import CursorParams, CursorPage

from repositories.sqlalchemy.datasource import Datasource
from repositories.sqlalchemy.datastore import Datastore
from repositories.sqlalchemy.agent_datastore import AgentDatastore
from repositories.sqlalchemy.base_repository import BaseRepository


from models.datastore import (
    CreateDatastoreSchema,
    UpdateDatastoreSchema,
    DatastoreSchema,
)

class DatastoreRepository(BaseRepository[
    CreateDatastoreSchema,
    UpdateDatastoreSchema,
    DatastoreSchema,
    Datastore,
]):
    @property
    def _table(self) -> Type[Datastore]:
        return Datastore

    @property
    def _schema(self) -> Type[DatastoreSchema]:
        return DatastoreSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(Datastore.created_at)
  
    async def paginate1(
        self,
        filter: Dict[str, Any],
        params: Optional[CursorParams] = None, 
    ) -> CursorPage[DatastoreSchema]:
        columns = [self._table.__dict__[col.name] for col in self._table.__table__.columns]
        query = (select(*columns, func.count(distinct(AgentDatastore.id)).label('agent_count'), func.count(distinct(Datasource.id)).label('datasource_count'))
            .where(Datastore.org_id == filter['org_id'])
            .outerjoin(AgentDatastore, self._table.id == AgentDatastore.datastore_id)
            .outerjoin(Datasource, self._table.id == Datasource.datastore_id)    
        )

        query = query.group_by(self._table.id)

        return await super().paginate(query, params)