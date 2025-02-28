from typing import Optional
from fastapi import APIRouter, Depends
from models.prompt import *
from services.prompt_service import PromptService
from schemas.pagination import CursorPage, CursorParams

from api.dependencies.auth import get_org_id
from .dto.prompt import *

router = APIRouter()
from uuid import UUID



@router.post("", status_code=201, response_model=PromptSchema)
async def create_a_prompt(
    data: CreatePromptSchema,
    prompt_service: PromptService = Depends(PromptService),
):
    return await prompt_service.create(data)

@router.get("/{prompt_id}", response_model=Optional[PromptSchema])
async def retrieve_a_prompt(
    prompt_id: UUID,
    prompt_service: PromptService = Depends(PromptService),
):
    return await prompt_service.get_by_id(prompt_id)

@router.patch("/{prompt_id}", response_model=PromptSchema)
async def update_a_prompt(
    prompt_id: UUID,
    data: UpdatePromptSchema,
    prompt_service: PromptService = Depends(PromptService),
):
    return await prompt_service.update_by_id(prompt_id, data)

@router.delete("/{prompt_id}", status_code=204)
async def delete_a_prompt(
    prompt_id: UUID,
    prompt_service: PromptService = Depends(PromptService),
):
    return await prompt_service.delete_by_id(prompt_id)

@router.get("", response_model=CursorPage[PromptSchema])
async def list_prompts(
    params: CursorParams = Depends(),
    prompt_service: PromptService = Depends(PromptService),
    org_id: str = Depends(get_org_id),
):
    """prompts list"""
    _filter = {
        "org_id": org_id,
    }
    return await prompt_service.paginate(_filter, params)