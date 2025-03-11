from typing import Optional, List
from fastapi import APIRouter, Depends, Request, Query
from services.user_service import UserService
from services.conversation_service import ConversationService
from security.auth0.auth import Auth0User
from api.dependencies.auth import get_auth_user
from models.user import UserSchema, CreateUserSchema, UpdateUserSchema
from models.conversation import *

from schemas.pagination import CursorParams, CursorPage

from uuid import UUID

router = APIRouter()



@router.patch("/me", status_code=201, response_model=UserSchema)
async def update_a_user(
    request: Request,
    data: UpdateUserSchema,
    user_service: UserService = Depends(UserService),
):
    return await user_service.update_by_id(request.state.api_key.user_id, data)


@router.get("/me", status_code=201, response_model=Optional[UserSchema])
async def get_profile(
    request: Request,
    user_service: UserService = Depends(UserService),
):
    return await user_service.get_by_id(request.state.api_key.user_id)

### organizations
from models.org import OrgSchema

@router.get("/me/orgs", response_model=List[OrgSchema], response_model_exclude_unset=True)
async def list_orgs(
    request: Request,
    user_id: UUID,
    user_service: UserService = Depends(UserService),
):
    return await user_service.list_orgs_by_user(request.state.api_key.user_id)


@router.get("/{user_id}/conversations", response_model=CursorPage[ConversationSchema], response_model_exclude_unset=True)
async def list_conversations(
    request: Request,
    params: CursorParams = Depends(None),
    conversation_service: ConversationService = Depends(ConversationService),
):
    """conversations list"""
    filter = ConversationFilter(
       user_id=request.state.api_key.user_id,
    )
    return await conversation_service.paginate(filter, params)
