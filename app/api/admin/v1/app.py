from fastapi import APIRouter, Depends
from models.wf_app import *
from services.app_service import AppService
from schemas.pagination import CursorPage, CursorParams
from typing import Optional



router = APIRouter()
from uuid import UUID



@router.post("", status_code=201, response_model=AppSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def create_a_app(
    app: CreateAppSchema,
    app_service: AppService = Depends(AppService),
):
    return await app_service.create(app)

@router.get("/{app_id}", response_model=Optional[AppSchema], response_model_exclude_none=True, response_model_exclude_unset=True)
async def retrieve_a_app(
    app_id: UUID,
    app_service: AppService = Depends(AppService),
):
    app = await app_service.get_by_id(app_id)
    # sanatize(app)
    return app

@router.patch("/{app_id}", response_model=AppSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def update_a_app(
    app_id: UUID,
    data: UpdateAppSchema,
    app_service: AppService = Depends(AppService),
):
    return await app_service.update_by_id(app_id, data)

@router.delete("/{app_id}", status_code=204, response_model_exclude_none=True, response_model_exclude_unset=True)
async def delete_a_app(
    app_id: UUID,
    app_service: AppService = Depends(AppService),
):
    return await app_service.delete_by_id(app_id)

@router.get("", response_model=CursorPage[AppSchema], response_model_exclude_none=True, response_model_exclude_unset=True)
async def list_apps(
    params: CursorParams = Depends(),
    filter: AppFilter = Depends(),
    app_service: AppService = Depends(AppService),
):
    """获取 apps 列表"""
    return await app_service.paginate(filter, params)