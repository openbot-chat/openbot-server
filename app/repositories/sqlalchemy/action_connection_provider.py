from sqlalchemy import Column, String, Text, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base_entity import TimestampedBase
from .connection_provider import ConnectionProvider


class ActionConnectionProvider(TimestampedBase):
    __tablename__ = "action_connection_providers"
    action_id = Column(UUID(as_uuid=True), ForeignKey('actions.id', ondelete="CASCADE"), nullable=False)
    action = relationship("Action", foreign_keys=[action_id], lazy="select")
    connection_provider_id = Column(UUID(as_uuid=True), ForeignKey('credentials_types.id', ondelete="CASCADE"), nullable=False)
    connection_provider = relationship(ConnectionProvider, foreign_keys=[connection_provider_id], lazy="selectin")
    options = Column(JSON, nullable=True)