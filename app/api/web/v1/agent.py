from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Request, HTTPException, status
from services.agent_service import AgentService
from services.tool_service import ToolService
from services.agent_tool_service import AgentToolService
from services.org_service import OrgService
from security.auth0.auth import Auth0User
from api.dependencies.auth import get_auth_user
from vectorstore import Document
from models.api import DeleteResponse
from models.agent import (
    AgentSchema, 
    CreateAgentSchema, 
    UpdateAgentSchema, 
    Visibility,
)
from models.agent_datastore import CreateAgentDatastoreSchema
from models.agent_tool import AgentToolFilter, CreateAgentToolSchema, UpdateAgentToolSchema
from uuid import UUID
from schemas.pagination import CursorParams, CursorPage
from vectorstore.datastore_manager import DatastoreManager
from config import (
    DEFAULT_QDRANT_OPTIONS
)
from api.dtos.agent import PublicAgentDTO, AgentFilter, CreateAgentToolDTO, AgentSayRequest



router = APIRouter()


@router.get("/{agent_id}", status_code=status.HTTP_200_OK, response_model=Optional[AgentSchema], response_model_exclude_unset=True, response_model_exclude_none=True, response_model_by_alias=False)
async def get_a_agent(
    request: Request,
    agent_id: UUID,
    agent_service: AgentService = Depends(AgentService),
    org_service: OrgService = Depends(OrgService),
    user: Optional[Auth0User] = Depends(get_auth_user),
):  
    agent = await agent_service.get_by_id(agent_id)
    if not agent:
        return None

    # 判断 member 存在否
    member = None
    if user is not None:
        member = await org_service.get_member(agent.org_id, user.id)

    if member is not None:
        return agent
    else:
        if agent.visibility == Visibility.PUBLIC:
            del agent.options
            return agent
        else:
            return None

@router.get("/by-identifier/{identifier}", status_code=status.HTTP_200_OK, response_model=Optional[PublicAgentDTO], response_model_exclude_unset=True, response_model_exclude_none=True, response_model_by_alias=False)
async def get_a_agent_by_identifier(
    request: Request,
    identifier: str,
    agent_service: AgentService = Depends(AgentService),
    user: Auth0User = Depends(get_auth_user),
):
    agent = await agent_service.get_by_identifier(identifier)
    if not agent:
        return None

    return PublicAgentDTO(
        id=agent.id,
        identifier=agent.identifier,
        avatar=agent.avatar,
        voice=agent.voice,
        name=agent.name,
        instructions=agent.instructions,
    )


# @router.post("", status_code=status.HTTP_201_CREATED, response_model=AgentSchema, response_model_exclude_unset=True, response_model_exclude_none=True)
async def create_a_agent(
    request: Request,
    data: CreateAgentSchema,
    agent_service: AgentService = Depends(AgentService),
    user: Auth0User = Depends(get_auth_user),
):
    return await agent_service.create(data)

# @router.patch("/{agent_id}", response_model=AgentSchema)
async def update_a_agent(
    request: Request,
    agent_id: UUID,
    agent: UpdateAgentSchema,
    agent_service: AgentService = Depends(AgentService),
    user: Auth0User = Depends(get_auth_user),
):
    return await agent_service.update_by_id(agent_id, agent)

# @router.get("", response_model=CursorPage[AgentSchema], response_model_exclude_unset=True)
async def list(
    request: Request,
    filter: AgentFilter = Depends(),
    params: CursorParams = Depends(),
    agent_service: AgentService = Depends(AgentService),
    user: Auth0User = Depends(get_auth_user),
):
    if not filter.org_id and filter.visibility != Visibility.PUBLIC:
        return CursorPage.create(
            items=[],
            params=params,
        )

    f = filter.dict(exclude_unset=True, exclude_none=True)

    page =  await agent_service.paginate(f, params=params)
    for item in page.items:
        del item.org_id
        del item.options

    return page

# @router.delete("/{agent_id}", response_model=AgentSchema)
async def delete_a_agent(
    request: Request,
    agent_id: UUID,
    agent_service: AgentService = Depends(AgentService),
    user: Auth0User = Depends(get_auth_user),
):
    return await agent_service.delete_by_id(agent_id)



# @router.post("/{agent_id}/tools", status_code=201, response_model=AgentToolSchema)
async def add_a_tool(
  request: Request,
  agent_id: UUID,
  data: CreateAgentToolDTO,
  tool_service: ToolService = Depends(ToolService),
  agent_tool_service: AgentToolService = Depends(AgentToolService),
  user: Auth0User = Depends(get_auth_user),
):
    tool = await tool_service.get_by_id(data.tool_id)
    if tool is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")

    agent_tool = await agent_tool_service.create(CreateAgentToolSchema(
        **data.dict(),
        agent_id=agent_id,
    ))

    docs = [Document(
        text=tool.description, 
        metadata={
            "source": tool.name, 
            "source_id": str(agent_tool.id),
            "author": str(agent_id),
        }
    )]
    
    collection_name = f'agent_tools'
    vectorstore = DatastoreManager.get('qdrant', DEFAULT_QDRANT_OPTIONS)
    await vectorstore.upsert(collection_name, docs)

    return agent_tool

# @router.patch("/{agent_id}/tools/{agent_tool_id}", status_code=status.HTTP_200_OK, response_model=AgentToolSchema)
async def update_a_tool(
  agent_id: UUID,
  agent_tool_id: UUID,
  data: UpdateAgentToolSchema,
  agent_tool_service: AgentToolService = Depends(AgentToolService),
  user: Auth0User = Depends(get_auth_user),
):
    agent_tool = await agent_tool_service.get_by_id(agent_tool_id)
    if agent_tool is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AgentTool not found")

    if agent_tool.agent_id != agent_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AgentTool not found for agent")        

    return await agent_tool_service.update_by_id(agent_tool_id, data)


# @router.delete("/{agent_id}/tools/{agent_tool_id}", status_code=status.HTTP_200_OK, response_model=DeleteResponse)
async def remove_a_tool(
  request: Request,
  agent_id: UUID,
  agent_tool_id: UUID,
  agent_tool_service: AgentToolService = Depends(AgentToolService),
  user: Auth0User = Depends(get_auth_user),
):
    await agent_tool_service.delete_one(agent_id, agent_tool_id);

    return DeleteResponse(success=True)



# @router.get("/{agent_id}/tools", response_model=CursorPage[AgentToolSchema])
async def list_tools_of_agent(
    request: Request,
    agent_id: UUID,
    params: CursorParams = Depends(),
    agent_tool_service: AgentToolService = Depends(AgentToolService),
    user: Auth0User = Depends(get_auth_user),
):
    filter = AgentToolFilter(
        agent_id=agent_id,
    )
    return await agent_tool_service.paginate(filter, params)



from models.voice import SayRequest, SayResponse
from services.voice_service import VoiceService

@router.post("/{agent_id}/voices/say", response_model=SayResponse, response_model_exclude_unset=True, response_model_exclude_none=True)
async def say(
    req: AgentSayRequest,
    agent_id: UUID,
    agent_service: AgentService = Depends(AgentService),
    voice_service: VoiceService = Depends(VoiceService)
):
    agent = await agent_service.get_by_id(agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    voice = agent.voice
    if not voice:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Agent voice not set")


    if not voice.options:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Agent voice not enabled")

    if not voice.options.get('enabled', False):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Agent voice not enabled")

    req1 = SayRequest(
        provider = voice.provider,
        identifier = voice.identifier,
        style = voice.style or req.style,
        pitch = voice.pitch or req.pitch,
        rate = voice.rate or req.rate,
        volume= voice.volume or req.volume,
        format = req.format,
        text = req.text,
    )

    return await voice_service.say(req1)


# @router.post("/{agent_id}/datastores/{datastore_id}", response_model=AgentDatastoreSchema)
async def bind_datastore(
    request: Request,
    agent_id: UUID,
    datastore_id: UUID,
    agent_service: AgentService = Depends(AgentService),
    user: Auth0User = Depends(get_auth_user),
):
    return await agent_service.bind_datastore(CreateAgentDatastoreSchema(
        agent_id=agent_id,
        datastore_id=datastore_id,
    ))

# @router.delete("/{agent_id}/datastores/{datastore_id}", response_model=AgentDatastoreSchema)
async def unbind_datastore(
    request: Request,
    agent_id: UUID,
    datastore_id: UUID,
    agent_service: AgentService = Depends(AgentService),
    user: Auth0User = Depends(get_auth_user),
):
    return await agent_service.unbind_datastore(agent_id, datastore_id)

# @router.get("/{agent_id}/datastores", response_model=CursorPage[AgentDatastoreSchema])
async def list_datastores(
    request: Request,
    agent_id: UUID,
    params: CursorParams = Depends(),
    agent_service: AgentService = Depends(AgentService),
    user: Auth0User = Depends(get_auth_user),
):
    return await agent_service.list_datastores(agent_id, params)