from typing import Optional
from fastapi import APIRouter, Depends
from models import prompt as prompt_schemas
from services.prompt_service import PromptService
from schemas.pagination import CursorPage, CursorParams
from security.auth0.auth import Auth0User
from api.dependencies.auth import get_auth_user


router = APIRouter()
from uuid import UUID

@router.post("", status_code=201, response_model=prompt_schemas.PromptSchema)
async def create_a_prompt(
  prompt: prompt_schemas.CreatePromptSchema,
  prompt_service: PromptService = Depends(PromptService),
  user: Auth0User = Depends(get_auth_user),
):
  result = await prompt_service.create(prompt)
  return result

@router.get("/{prompt_id}", response_model=Optional[prompt_schemas.PromptSchema])
async def retrieve_a_prompt(
  prompt_id: UUID,
  prompt_service: PromptService = Depends(PromptService),
  user: Auth0User = Depends(get_auth_user),
):
  return await prompt_service.get_by_id(prompt_id)

@router.patch("/{prompt_id}", response_model=prompt_schemas.PromptSchema)
async def update_a_prompt(
  prompt_id: UUID,
  data: prompt_schemas.UpdatePromptSchema,
  prompt_service: PromptService = Depends(PromptService),
  user: Auth0User = Depends(get_auth_user),
):
  return await prompt_service.update_by_id(prompt_id, data)

@router.delete("/{prompt_id}", status_code=204)
async def delete_a_prompt(
  prompt_id: UUID,
  prompt_service: PromptService = Depends(PromptService),
):
  return await prompt_service.delete_by_id(prompt_id)

@router.get("", response_model=CursorPage[prompt_schemas.PromptSchema])
async def list_prompts(
  params: CursorParams = Depends(),
  prompt_service: PromptService = Depends(PromptService),
  user: Auth0User = Depends(get_auth_user),
):
  """获取 prompts 列表"""
  print('user', f'{user}')
  return await prompt_service.paginate(params)
