from typing import Type, Dict, Optional, Any

from sqlalchemy.orm import InstrumentedAttribute, subqueryload, joinedload
from sqlalchemy import desc
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.sql import Select

from .agent import Agent
from repositories.sqlalchemy.base_repository import BaseRepository
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from uuid import UUID
from schemas.pagination import CursorParams, CursorPage



from models.agent import (
    CreateAgentSchema,
    UpdateAgentSchema,
    AgentSchema,
)

class AgentRepository(BaseRepository[
    CreateAgentSchema,
    UpdateAgentSchema,
    AgentSchema,
    Agent,
]):
    @property
    def _table(self) -> Type[Agent]:
        return Agent

    @property
    def _schema(self) -> Type[AgentSchema]:
        return AgentSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(Agent.created_at)
  
    async def get_by_id(self, entry_id: UUID) -> Optional[AgentSchema]:
        query = select(self._table).where(self._table.id == entry_id)
        """
        query = query.options(
            subqueryload(self._table.datastores).subqueryload(AgentDatastore.datastore)
        )
        
        query = query.options(
            joinedload(self._table.datastores).
            joinedload(AgentDatastore.datastore)
        )
        """

        entry = (await self._db_session.execute(query)).scalar_one_or_none()
        if not entry:
            return None

        return self._schema.from_orm(entry)

    async def get_by_identifier(self, identifier: str) -> Optional[AgentSchema]:
        query = select(self._table).where(self._table.identifier == identifier)
        entry = (await self._db_session.execute(query)).scalar_one_or_none()
        if not entry:
            return None

        return self._schema.from_orm(entry)

    async def paginate1(self, filter: Dict[str, Any], params: Optional[CursorParams] = None) -> CursorPage[AgentSchema]:
        query = select(self._table).order_by(self._order_by)

        if 'visibility' in filter:
            query = query.where(
                Agent.visibility == filter['visibility'].value,
            )

        if 'org_id' in filter:
            query = query.where(
                Agent.org_id == filter['org_id'],
            )

        return await super().paginate(query, params)