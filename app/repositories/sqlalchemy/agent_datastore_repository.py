from typing import Type, List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc

from .agent_datastore import AgentDatastore
from repositories.sqlalchemy.base_repository import BaseRepository
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.sql import Select
from schemas.pagination import CursorParams, CursorPage



from models.agent_datastore import (
    CreateAgentDatastoreSchema,
    UpdateAgentDatastoreSchema,
    AgentDatastoreSchema,
)

class AgentDatastoreRepository(BaseRepository[
    CreateAgentDatastoreSchema,
    UpdateAgentDatastoreSchema,
    AgentDatastoreSchema,
    AgentDatastore,
]):
    @property
    def _table(self) -> Type[AgentDatastore]:
        return AgentDatastore

    @property
    def _schema(self) -> Type[AgentDatastoreSchema]:
        return AgentDatastoreSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(AgentDatastore.created_at)
  
    async def delete(self, agent_id: UUID, datastore_id: UUID) -> AgentDatastoreSchema:
        result = await self._db_session.execute(
            select(self._table).where(
                self._table.agent_id == agent_id,
                self._table.datastore_id == datastore_id,
            )
        )

        entry = result.scalar()
        if not entry:
            raise HTTPException(status_code=404, detail="Object not found")

        await self._db_session.delete(entry)
        await self._db_session.commit()

        return AgentDatastoreSchema.from_orm(entry)

    async def paginate1(
        self,
        agent_id: UUID,
        params: Optional[CursorParams] = None,
    ) -> CursorPage[AgentDatastoreSchema]:
        query = select(AgentDatastore).where(
            AgentDatastore.agent_id == agent_id,
        ).order_by(AgentDatastore.created_at.desc())

        return await super().paginate(query, params)