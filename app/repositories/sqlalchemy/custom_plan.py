from sqlalchemy import Column, String, Text, JSON, DateTime, Integer, ForeignKey, BigInteger, Boolean
from db.base_entity import TimestampedBase
from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, func, String



class CustomPlan(TimestampedBase):
    __tablename__ = "custom_plans"

    external_id = Column(String, nullable=False, index=True, unique=True)
    claimed_at = Column(DateTime(), nullable=False, server_default=func.now())
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    price = Column(BigInteger)
    currency = Column(String)
    is_yearly = Column(Boolean, default=False)
    org_id = Column(String, unique=True, index=True)
    storage_limit = Column(BigInteger, nullable=True, default=0)
    token_limit = Column(BigInteger, nullable=True, default=0)
    chats_limit = Column(BigInteger, nullable=True, default=0)