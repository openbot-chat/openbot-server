from sqlalchemy import Column, Text, String, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from db.base_entity import TimestampedBase
from .datastore import Datastore
from .agent import Agent


class AgentDatastore(TimestampedBase):
    __tablename__ = "agent_datastores"
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id', ondelete="CASCADE"), nullable=False)
    agent = relationship(Agent, foreign_keys=[agent_id], lazy="select", back_populates="datastores")
    datastore_id = Column(UUID(as_uuid=True), ForeignKey('datastores.id', ondelete="CASCADE"), nullable=False)
    datastore = relationship(Datastore, foreign_keys=[datastore_id], lazy="selectin")
    options = Column(JSON, nullable=True)