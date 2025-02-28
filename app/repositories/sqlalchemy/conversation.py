from sqlalchemy import Column, String, JSON
from db.base_entity import TimestampedBase
from sqlalchemy.dialects.postgresql import UUID



class Conversation(TimestampedBase):
    __tablename__ = "conversations"
    provider = Column(String, nullable=False)
    agent_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(String, nullable=True)
    visitor_id = Column(String, nullable=True)
    options = Column(JSON, nullable=True)