from typing import Type, List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc

from .agent_tool import AgentTool
from repositories.sqlalchemy.base_repository import BaseRepository
from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.sql import Select
from schemas.pagination import CursorParams, CursorPage

from models.agent_tool import (
    CreateAgentToolSchema,
    UpdateAgentToolSchema,
    AgentToolSchema,
    AgentToolFilter,
)

class AgentToolRepository(BaseRepository[
    CreateAgentToolSchema,
    UpdateAgentToolSchema,
    AgentToolSchema,
    AgentTool,
]):
    @property
    def _table(self) -> Type[AgentTool]:
        return AgentTool

    @property
    def _schema(self) -> Type[AgentToolSchema]:
        return AgentToolSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(AgentTool.created_at)

    async def paginate1(
      self,
      filter: AgentToolFilter,
      params: Optional[CursorParams] = None,
    ) -> CursorPage[AgentToolSchema]:
        query = select(AgentTool).order_by(AgentTool.created_at.desc())

        if filter.agent_id:
            query = query.where(AgentTool.agent_id == filter.agent_id)

        return await super().paginate(query, params)