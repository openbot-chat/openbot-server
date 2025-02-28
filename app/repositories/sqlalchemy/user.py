from sqlalchemy import Column, String, JSON, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID
from db.base_entity import TimestampedBase
from typing import List



class User(TimestampedBase):
    __tablename__ = "users"
    name = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    options = Column(JSON, nullable=True)
    email = Column(String, nullable=True, unique=True)
    accounts: Mapped[List["Account"]] = relationship("Account", back_populates="user", lazy="selectin")
    members: Mapped[List["OrgMember"]] = relationship("OrgMember", back_populates="user", lazy="selectin", cascade="save-update, merge, delete, delete-orphan")

class Account(TimestampedBase):
    __tablename__ = "accounts"
    user_id = Column(UUID, ForeignKey('users.id'), nullable=False)
    type = Column(String, nullable=False)
    provider: Mapped[str] = Column(String, nullable=False)
    providerAccountId: Mapped[str] = Column(String, nullable=False)
    refresh_token = Column(Text, nullable=True)
    access_token = Column(Text, nullable=True)
    expires_at = Column(Integer, nullable=True)
    token_type = Column(String, nullable=True)
    scope = Column(String, nullable=True)
    id_token = Column(Text, nullable=True)
    session_state = Column(String, nullable=True)
    oauth_token_secret = Column(String, nullable=True)
    oauth_token = Column(String, nullable=True)
    refresh_token_expires_in = Column(Integer, nullable=True)
    user: Mapped["User"] = relationship("User", back_populates="accounts", foreign_keys=[user_id], cascade="delete")