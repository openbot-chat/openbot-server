from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from schemas.pagination import CursorParams, CursorPage
from models.custom_plan import *
from services.custom_plan_service import CustomPlanService
from uuid import UUID
from typing import Optional



router = APIRouter()
from uuid import UUID

@router.post("", status_code=201, response_model=CustomPlanSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def create_a_custom_plan(
    custom_plan: CreateCustomPlanSchema,
    custom_plan_service: CustomPlanService = Depends(CustomPlanService),
):
    return await custom_plan_service.create(custom_plan)

@router.get("/{custom_plan_id}", response_model=Optional[CustomPlanSchema], response_model_exclude_none=True, response_model_exclude_unset=True)
async def retrieve_a_custom_plan(
    custom_plan_id: UUID,
    custom_plan_service: CustomPlanService = Depends(CustomPlanService),
):
    return await custom_plan_service.get_by_id(custom_plan_id)

@router.get("/by-org_id/{org_id}", response_model=Optional[CustomPlanSchema], response_model_exclude_none=True, response_model_exclude_unset=True)
async def get_a_custom_plan_by_org_id(
    org_id: str,
    custom_plan_service: CustomPlanService = Depends(CustomPlanService),
):
    return await custom_plan_service.get_by_org_id(org_id)

@router.get("/external/{external_id}", response_model=Optional[CustomPlanSchema], response_model_exclude_none=True, response_model_exclude_unset=True)
async def get_a_custom_plan_by_external_id(
    external_id: str,
    custom_plan_service: CustomPlanService = Depends(CustomPlanService),
):
    return await custom_plan_service.get_by_external_id(external_id)

@router.patch("/{custom_plan_id}", response_model=CustomPlanSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def update_a_custom_plan(
    custom_plan_id: UUID,
    updates: UpdateCustomPlanSchema,
    custom_plan_service: CustomPlanService = Depends(CustomPlanService),
):
    return await custom_plan_service.update_by_id(custom_plan_id, updates)

@router.delete("/{custom_plan_id}", status_code=204)
async def delete_a_custom_plan(
    custom_plan_id: UUID,
    custom_plan_service: CustomPlanService = Depends(CustomPlanService),
):
    await custom_plan_service.delete_by_id(custom_plan_id)

@router.get("", response_model=CursorPage[CustomPlanSchema], response_model_exclude_none=True, response_model_exclude_unset=True)
async def list_custom_plans(
    params: CursorParams = Depends(),
    custom_plan_id: UUID = Query(None),
    custom_plan_service: CustomPlanService = Depends(CustomPlanService),
):
    return await custom_plan_service.paginate(params=params)