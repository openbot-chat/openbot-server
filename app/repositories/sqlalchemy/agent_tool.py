from sqlalchemy import Column, String, Text, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base_entity import TimestampedBase
from .agent import Agent


class AgentTool(TimestampedBase):
    __tablename__ = "agent_tools"
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id', ondelete="CASCADE"), nullable=False)
    agent = relationship(Agent, foreign_keys=[agent_id], lazy="select")
    tool_id = Column(UUID(as_uuid=True), ForeignKey('tools.id', ondelete="CASCADE"), nullable=False)
    tool = relationship("Tool", foreign_keys=[tool_id], lazy="selectin")
    return_direct = Column(Boolean, default=False)
    options = Column(JSON, nullable=True)
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)