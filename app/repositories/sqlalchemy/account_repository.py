from typing import Type

from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy import desc

from .user import Account
from repositories.sqlalchemy.base_repository import BaseRepository


from models.account import (
    CreateAccountSchema,
    UpdateAccountSchema,
    AccountSchema,
)

class AccountRepository(BaseRepository[
    CreateAccountSchema,
    UpdateAccountSchema,
    AccountSchema,
    Account,
]):
    @property
    def _table(self) -> Type[Account]:
        return Account

    @property
    def _schema(self) -> Type[AccountSchema]:
        return AccountSchema

    @property
    def _order_by(self) -> InstrumentedAttribute:
        return desc(Account.created_at)

    async def upsert_by_provider(self, in_schema: UpdateAccountSchema) -> AccountSchema:
        return await self.upsert(in_schema, constraints=[Account.provider, Account.providerAccountId])