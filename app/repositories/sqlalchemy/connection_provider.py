from sqlalchemy import Column, Text, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from db.base_entity import TimestampedBase
from sqlalchemy.dialects.postgresql import UUID



class ConnectionProvider(TimestampedBase):
    __tablename__ = "credentials_types"
    name = Column(String, nullable=False)
    app_id = Column(UUID(as_uuid=True), ForeignKey('apps.id', ondelete="save-update, merge"), nullable=True)
    app = relationship("App", foreign_keys=[app_id], lazy="select")

    identifier = Column(String, nullable=False, unique=True) # unique
    type = Column(String, nullable=True)
    icon = Column(String, nullable=True)
    doc_url = Column(String, nullable=True)
    options = Column(JSON, nullable=True)