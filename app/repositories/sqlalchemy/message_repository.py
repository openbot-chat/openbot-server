from typing import Type, Optional

from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc, delete
from sqlalchemy.sql import Select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select
from repositories.sqlalchemy.message import Message
from repositories.sqlalchemy.base_repository import BaseRepository
from models.message import MessageFilter
from schemas.pagination import CursorParams, CursorPage

from models.message import (
    CreateMessageSchema,
    UpdateMessageSchema,
    MessageSchema,
)

class MessageRepository(BaseRepository[
    CreateMessageSchema,
    UpdateMessageSchema,
    MessageSchema,
    Message,
]):
    @property
    def _table(self) -> Type[Message]:
        return Message

    @property
    def _schema(self) -> Type[MessageSchema]:
        return MessageSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(Message.created_at)

    def fill_filter(self, query: Select, filter: MessageFilter):
        if filter.agent_id:
            query = query.where(
                Message.agent_id == filter.agent_id,
            )
        
        if filter.conversation_id:
            query = query.where(
                Message.conversation_id == filter.conversation_id,
            )

        return query

    async def list_messages(
        self,
        filter: MessageFilter,
        params: Optional[CursorParams] = None,
    ) -> CursorPage[MessageSchema]:
        query = select(Message).order_by(Message.created_at.desc())
        query = self.fill_filter(query, filter)

        return await super().paginate(query, params)

    async def count1(
        self,
        filter: MessageFilter,
    ) -> int:
        query = select(Message)
        query = self.fill_filter(query, filter)

        return await super().count(query)

    async def delete_by_conversation_id(self, conversation_id: str, autocommit: bool = True):
        await self._db_session.execute(
            delete(Message).where(
                Message.conversation_id == conversation_id,
            )
        )

        if autocommit:
            await self._db_session.commit()