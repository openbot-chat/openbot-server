from sqlalchemy import Column, String, Text
from db.base_entity import TimestampedBase



class Message(TimestampedBase):
    __tablename__ = "messages"
    agent_id = Column(String, nullable=False, index=True)
    conversation_id = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)
    text = Column(Text, nullable=False)