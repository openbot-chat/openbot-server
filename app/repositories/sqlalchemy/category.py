from sqlalchemy import Column, String, Text, JSON
from db.base_entity import TimestampedBase


class Category(TimestampedBase):
    __tablename__ = "categories"
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String, nullable=True)
    options = Column(JSON, nullable=True)