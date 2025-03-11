from sqlalchemy import Column, String, Text, JSON, Boolean, ForeignKey
from db.base_entity import TimestampedBase, MultiTenantBase
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID
from typing import List
from .action import *
from .connection_provider import *



class App(TimestampedBase, MultiTenantBase):
    __tablename__ = "apps"
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String, nullable=True)
    theme = Column(String, nullable=True)
    options = Column(JSON, nullable=True)
    actions: Mapped[List[Action]] = relationship(
        Action,
        back_populates="app", 
        lazy="selectin", 
        cascade="save-update, merge, delete, delete-orphan",
    )
    connections: Mapped[List[ConnectionProvider]] = relationship(
        ConnectionProvider, 
        back_populates="app",
        lazy="selectin", 
        cascade="save-update, merge",
    )