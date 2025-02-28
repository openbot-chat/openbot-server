from fastapi import APIRouter, Depends, Request
from services.agent_service import AgentService
from models.agent import (
    AgentSchema, 
    Visibility,
)
from schemas.pagination import CursorParams, CursorPage

router = APIRouter()

@router.get("/agents", response_model=CursorPage[AgentSchema])
async def list_agents(
    request: Request,
    params: CursorParams = Depends(),
    agent_service: AgentService = Depends(AgentService),
):
    return await agent_service.paginate(
        {
            "visibility": Visibility.PUBLIC
        },
        params,
    )