from typing import Type, Optional

from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc
from sqlalchemy.sql import Select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select
from repositories.sqlalchemy.conversation import Conversation
from repositories.sqlalchemy.base_repository import BaseRepository
from models.conversation import ConversationFilter
from schemas.pagination import CursorParams, CursorPage

from models.conversation import (
    CreateConversationSchema,
    UpdateConversationSchema,
    ConversationSchema,
)

class ConversationRepository(BaseRepository[
    CreateConversationSchema,
    UpdateConversationSchema,
    ConversationSchema,
    Conversation,
]):
    @property
    def _table(self) -> Type[Conversation]:
        return Conversation

    @property
    def _schema(self) -> Type[ConversationSchema]:
        return ConversationSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(Conversation.created_at)

    def fill_filter(self, query: Select, filter: ConversationFilter):
        if filter.agent_id:
            query = query.where(
                Conversation.agent_id == filter.agent_id,
            )
        
        if filter.provider:
            query = query.where(
                Conversation.provider == filter.provider,
            )
        
        if filter.user_id:
            query = query.where(
                Conversation.user_id == filter.user_id,
            )
        return query

    async def paginate1(
        self,
        filter: ConversationFilter,
        params: Optional[CursorParams] = None,
    ) -> CursorPage[ConversationSchema]:
        query = select(Conversation).order_by(Conversation.created_at.desc())
        query = self.fill_filter(query, filter)

        return await super().paginate(query, params)

    async def count1(
        self,
        filter: ConversationFilter,
    ) -> int:
        query = select(Conversation)
        query = self.fill_filter(query, filter)

        return await super().count(query)