from typing import Any, Optional, Sequence, Type, List

from sqlalchemy.orm import InstrumentedAttribute, subqueryload
from sqlalchemy import desc

from .user import User, Account
from .org import Org, OrgMember
from repositories.sqlalchemy.base_repository import BaseRepository
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from uuid import UUID
from sqlalchemy.future import select

from models.org import (
    OrgSchema,
)

from models.user import (
    CreateUserSchema,
    UpdateUserSchema,
    UserSchema,
)

class UserRepository(BaseRepository[
    CreateUserSchema,
    UpdateUserSchema,
    UserSchema,
    User,
]):
    @property
    def _table(self) -> Type[User]:
        return User

    @property
    def _schema(self) -> Type[UserSchema]:
        return UserSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(User.created_at) 
 

    async def get_by_id(self, entry_id: UUID) -> Optional[UserSchema]:
        query = select(self._table).where(self._table.id == entry_id)
        query = query.options(
            subqueryload(User.accounts)
        )
        
        query = query.options(
            subqueryload(User.members).
            subqueryload(OrgMember.org)
        )

        entry = (await self._db_session.execute(query)).scalar_one_or_none()
        if not entry:
            return None
        
        await self._db_session.refresh(entry)

        return self._schema.from_orm(entry)

    async def get_by_provider_account_id(self, provider: str, account_id: str) -> Optional[UserSchema]:
        result = await self._db_session.execute(
            select(User).join(Account).filter(
              Account.provider == provider, 
              Account.providerAccountId == account_id,
            )
        )

        entry = result.scalar_one_or_none()

        if not entry:
            return None
        return self._schema.from_orm(entry)

    async def get_by_email(self, email: str) -> Optional[UserSchema]:
        result = await self._db_session.execute(
            select(User).where(
              User.email == email,
            )
        )

        entry = result.scalars().first()

        if not entry:
          return None
        return self._schema.from_orm(entry)


    async def get_by_ids(self, ids: List[UUID]) -> List[UserSchema]:
        return await self._db_session.run_sync(
            lambda sync_session: sync_session.query(
              User
            ).filter(
              User.id.in_(ids)
            ).all()
        )

    async def list_orgs_by_user(self, user_id: UUID) -> List[OrgSchema]:
        response = await self._db_session.execute(
            select(Org).join(OrgMember).filter(
              OrgMember.user_id == user_id,
            ).order_by(Org.created_at.asc())
        )
        entries = response.scalars().all()

        return [OrgSchema.from_orm(entry) for entry in entries]
