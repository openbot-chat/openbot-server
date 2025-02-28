from sqlalchemy import Column, String, Text, JSON, Boolean, ForeignKey
from db.base_entity import TimestampedBase, MultiTenantBase
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID



class Tool(TimestampedBase, MultiTenantBase):
    __tablename__ = "tools"
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String, nullable=True)
    return_direct = Column(Boolean, default=False)
    options = Column(JSON, nullable=True)
    toolkit_id = Column(UUID(as_uuid=True), ForeignKey('toolkits.id', ondelete="CASCADE"), nullable=True)
    toolkit = relationship("Toolkit", foreign_keys=[toolkit_id], lazy="select", back_populates="tools")
    