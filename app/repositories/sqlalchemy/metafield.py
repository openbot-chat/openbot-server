from sqlalchemy import Column, String, Text
from db.base_entity import TimestampedBase



class Metafield(TimestampedBase):
    __tablename__ = "metafields"
    owner_type = Column(String, nullable=False, index=True)
    owner_id = Column(String, nullable=False, index=True)
    namespace = Column(String, nullable=False, index=True)
    key = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    description = Column(Text, nullable=True)