from typing import List, Optional
from fastapi import APIRouter, Depends, Request, HTTPException, Query
from services.avatar_service import AvatarService
from models.avatar import AvatarSchema, CreateAvatarSchema, UpdateAvatarSchema
from uuid import UUID
from schemas.pagination import CursorPage, CursorParams

router = APIRouter()


@router.get("/{avatar_id}", status_code=201, response_model=AvatarSchema)
async def get_a_avatar(
  avatar_id: UUID,
  avatar_service: AvatarService = Depends(AvatarService),
):  
  return await avatar_service.get_by_id(avatar_id)



@router.post("", status_code=201, response_model=AvatarSchema)
async def create_a_avatar(
  data: CreateAvatarSchema,
  avatar_service: AvatarService = Depends(AvatarService),
):
  return await avatar_service.create(data)

@router.patch("/{avatar_id}", response_model=AvatarSchema)
async def update_a_avatar(
  request: Request,
  avatar_id: UUID,
  data: UpdateAvatarSchema,
  avatar_service: AvatarService = Depends(AvatarService),
):
  return await avatar_service.update_by_id(avatar_id, data)

@router.get("", response_model=CursorPage[AvatarSchema], response_model_exclude_unset=True, response_model_exclude_none=True)
async def get_paginated_list(
  request: Request,
  params: Optional[CursorParams] = Depends(),
  avatar_service: AvatarService = Depends(AvatarService),
):
  return  await avatar_service.paginate(params)