from typing import Optional
from fastapi import APIRouter, Depends, Request, status
from services.account_service import AccountService

from security.auth0.auth import Auth0User

from api.dependencies.auth import get_auth_user
from models.account import AccountSchema, CreateAccountSchema, UpdateAccountSchema

from uuid import UUID

router = APIRouter()



@router.post("", status_code=status.HTTP_201_CREATED, response_model=AccountSchema)
async def create_a_account(
  request: Request,
  account: CreateAccountSchema,
  account_service: AccountService = Depends(AccountService),
  auth_user: Auth0User = Depends(get_auth_user),
):
  return await account_service.create(account)

@router.patch("/{account_id}", status_code=status.HTTP_200_OK, response_model=AccountSchema)
async def update_a_account(
  request: Request,
  account_id: UUID,
  data: UpdateAccountSchema,
  account_service: AccountService = Depends(AccountService),
  auth_user: Auth0User = Depends(get_auth_user),
):
  return await account_service.update_by_id(account_id, data)


@router.get("/{account_id}", status_code=status.HTTP_200_OK, response_model=Optional[AccountSchema])
async def get_a_account(
  request: Request,
  account_id: UUID,
  account_service: AccountService = Depends(AccountService),
  user: Auth0User = Depends(get_auth_user),
):
  return await account_service.get_by_id(account_id)