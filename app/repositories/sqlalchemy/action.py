from sqlalchemy import Column, String, Text, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from db.base_entity import TimestampedBase
from typing import List
from .action_connection_provider import *

class Action(TimestampedBase):
    __tablename__ = "actions"
    app_id = Column(UUID(as_uuid=True), ForeignKey('apps.id', ondelete="CASCADE"), nullable=False)
    app = relationship("App", foreign_keys=[app_id], lazy="select")
    connection_providers: Mapped[List[ActionConnectionProvider]] = relationship(
        "ActionConnectionProvider", 
        back_populates="action", 
        lazy="selectin", 
        cascade="save-update, merge, delete, delete-orphan"
    )
    options = Column(JSON, nullable=True)
    name = Column(String, nullable=True)
    identifier = Column(String, nullable=True)
    description = Column(Text, nullable=True)