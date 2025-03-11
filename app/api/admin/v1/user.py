from typing import Optional, List
from fastapi import APIRouter, Depends, Request, Query
from services.user_service import UserService
from services.conversation_service import ConversationService
from models.user import UserSchema, CreateUserSchema, UpdateUserSchema
from models.conversation import *

from schemas.pagination import CursorParams, CursorPage

from uuid import UUID

router = APIRouter()



@router.post("", status_code=201, response_model=UserSchema)
async def create_a_user(
    request: Request,
    user: CreateUserSchema,
    user_service: UserService = Depends(UserService),
):
    return await user_service.create(user)

@router.patch("/{user_id}", status_code=201, response_model=UserSchema)
async def update_a_user(
    request: Request,
    user_id: UUID,
    data: UpdateUserSchema,
    user_service: UserService = Depends(UserService),
):
    return await user_service.update_by_id(user_id, data)


@router.get("/{id}", status_code=201, response_model=Optional[UserSchema])
async def get_a_user(
    request: Request,
    id: UUID,
    user_service: UserService = Depends(UserService),
):
    return await user_service.get_by_id(id)

@router.get("/by-provider/{provider}/account_id/{account_id}", status_code=201, response_model=Optional[UserSchema])
async def get_user_by_provider_account_id(
    request: Request,
    provider: str,
    account_id: str,
    user_service: UserService = Depends(UserService),
):
    return await user_service.get_by_provider_account_id(provider, account_id)

@router.get("/by-email/{email}", status_code=201, response_model=Optional[UserSchema])
async def get_user_by_email(
    request: Request,
    email: str,
    user_service: UserService = Depends(UserService),
):
    return await user_service.get_by_email(email)


@router.get("", response_model=CursorPage[UserSchema], response_model_exclude_unset=True)
async def list(
    request: Request,
    params: CursorParams = Depends(),
    user_service: UserService = Depends(UserService),
):
    page =  await user_service.paginate(params=params)
    for item in page.items:
        del item.options

    return page



### organizations
from models.org import OrgSchema

@router.get("/{user_id}/orgs", response_model=List[OrgSchema], response_model_exclude_unset=True)
async def list_orgs(
    request: Request,
    user_id: UUID,
    user_service: UserService = Depends(UserService),
):
    return await user_service.list_orgs_by_user(user_id)


@router.get("/{user_id}/conversations", response_model=CursorPage[ConversationSchema], response_model_exclude_unset=True)
async def list_conversations(
    user_id: UUID,
    params: CursorParams = Depends(None),
    conversation_service: ConversationService = Depends(ConversationService),
):
    """conversations list"""
    filter = ConversationFilter(
       user_id=user_id,
    )
    return await conversation_service.paginate(filter, params)
