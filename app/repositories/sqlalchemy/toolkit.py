from sqlalchemy import Column, String, Text, JSON
from sqlalchemy.orm import relationship, Mapped
from db.base_entity import TimestampedBase, MultiTenantBase
from typing import List
from .tool import *


class Toolkit(TimestampedBase, MultiTenantBase):
    """
        ToolKit - Used to group tools together
        Attributes:
            id(UUID) : id of the toolkit
            name(str) : name of the toolkit
            description(str) : description of the toolkit
            org_id(str) : org id of the to which tool config is related
    """
    __tablename__ = "toolkits"
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String, nullable=True)
    options = Column(JSON, nullable=True)
    tools: Mapped[List[Tool]] = relationship(
        Tool,
        back_populates="toolkit",
        lazy="selectin", 
        cascade="save-update, merge, delete"
    )