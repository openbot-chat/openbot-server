from fastapi import APIRouter, Depends
from models.connection_provider import *
from services.connection_provider_service import ConnectionProviderService
from schemas.pagination import CursorParams, CursorPage
from security.auth0.auth import Auth0User
from api.dependencies.auth import get_auth_user


router = APIRouter()
from uuid import UUID

@router.post("", status_code=201, response_model=ConnectionProviderSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def create_a_connection_provider(
    connection_provider: CreateConnectionProviderSchema,
    connection_provider_service: ConnectionProviderService = Depends(ConnectionProviderService),
    user: Auth0User = Depends(get_auth_user),
):
    return await connection_provider_service.create(connection_provider)

@router.get("/{connection_provider_id}", response_model=Optional[ConnectionProviderSchema], response_model_exclude_none=True, response_model_exclude_unset=True)
async def retrieve_a_connection_provider(
    connection_provider_id: UUID,
    connection_provider_service: ConnectionProviderService = Depends(ConnectionProviderService),
    user: Auth0User = Depends(get_auth_user),
):
    return await connection_provider_service.get_by_id(connection_provider_id)

@router.get("/by-identifier/{identifier}", response_model=Optional[ConnectionProviderSchema], response_model_exclude_none=True, response_model_exclude_unset=True)
async def retrieve_a_connection_provider_by_identifier(
    identifier: str,
    connection_provider_service: ConnectionProviderService = Depends(ConnectionProviderService),
    user: Auth0User = Depends(get_auth_user),
):
    return await connection_provider_service.get_by_identifier(identifier)


@router.patch("/{connection_provider_id}", response_model=ConnectionProviderSchema, response_model_exclude_none=True, response_model_exclude_unset=True)
async def update_a_connection_provider(
    connection_provider_id: UUID,
    data: UpdateConnectionProviderSchema,
    connection_provider_service: ConnectionProviderService = Depends(ConnectionProviderService),
    user: Auth0User = Depends(get_auth_user),
):
    return await connection_provider_service.update_by_id(connection_provider_id, data)

@router.delete("/{connection_provider_id}", status_code=204)
async def delete_a_connection_provider(
    connection_provider_id: UUID,
    connection_provider_service: ConnectionProviderService = Depends(ConnectionProviderService),
):
    await connection_provider_service.delete_by_id(connection_provider_id)

@router.get("", response_model=CursorPage[ConnectionProviderSchema], response_model_exclude_unset=True)
async def list_connection_providers(
    params: CursorParams = Depends(),
    filter: ConnectionFilter = Depends(),
    connection_provider_service: ConnectionProviderService = Depends(ConnectionProviderService),
    user: Auth0User = Depends(get_auth_user),
):
    return await connection_provider_service.paginate(filter, params=params)