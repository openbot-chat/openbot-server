from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID
from db.base_entity import TimestampedBase
from typing import List
from models.plan import Plan


class Org(TimestampedBase):
    __tablename__ = "orgs"
    members: Mapped[List["OrgMember"]] = relationship("OrgMember", back_populates="org", lazy="selectin", cascade="save-update, merge, delete, delete-orphan")
    name = Column(String, nullable=False)
    plan = Column(Enum(Plan), nullable=False, default=Plan.FREE)
    payment_customer_id = Column(String, nullable=True)
    icon = Column(String, nullable=True)

class OrgMember(TimestampedBase):
    __tablename__ = "org_members"
    user_id = Column(UUID, ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="members", foreign_keys=[user_id], lazy="selectin")
    org_id = Column(UUID, ForeignKey('orgs.id'), nullable=False)
    org: Mapped["Org"] = relationship("Org", back_populates="members", foreign_keys=[org_id], lazy="selectin")
    role = Column(String, nullable=False)