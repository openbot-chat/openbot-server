from sqlalchemy import Column, Text, String, JSON, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from db.base_entity import TimestampedBase, MultiTenantBase
from typing import List



# 有没有做 agent 的比较专业的项目，对标下它们的定义
class Agent(TimestampedBase, MultiTenantBase):
    __tablename__ = "agents"
    name = Column(String, nullable=False)
    avatar = Column(JSON, nullable=True)
    voice = Column(JSON, nullable=True)
    cognition = Column(JSON, nullable=True)    
    identifier = Column(String, nullable=True, index=True)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    options = Column(JSON, nullable=True, default={})
    metadata_ = Column('metadata', JSON, default={})
    visibility = Column(String, nullable=True, default="private")
    template_id = Column(UUID(as_uuid=True), nullable=True)
    creator_id = Column(String, nullable=True)
    datastores: Mapped[List["AgentDatastore"]] = relationship(
        "AgentDatastore",
        back_populates="agent",
        lazy="selectin", 
        cascade="save-update, merge, delete, delete-orphan"
    )
    tools: Mapped[List["AgentTool"]] = relationship(
        "AgentTool", 
        back_populates="agent", 
        lazy="selectin", 
        cascade="save-update, merge, delete, delete-orphan"
    )
