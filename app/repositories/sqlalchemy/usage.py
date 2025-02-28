from sqlalchemy import Column, Integer, String
from db.base_entity import TimestampedBase



# 理想情况应该用 cqrs 机制存储
class Usage(TimestampedBase):
    __tablename__ = "usages"
    org_id = Column(String, nullable=False, index=True)

    nb_tokens = Column(Integer, nullable=False, default=0)
    nb_uploaded_bytes = Column(Integer, nullable=False, default=0)