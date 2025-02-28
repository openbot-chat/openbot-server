from fastapi import HTTPException
from typing import List, Optional
from uuid import UUID
# from api.dependencies.repository import make_repository
from typing import Dict
from models import voice as voice_schemas
from models.locale import LocaleSchemaBase 
from schemas.pagination import CursorParams, CursorPage
from core.voice.providers import VoiceProvider, AzureVoiceProvider, PlayhtVoiceProvider


class VoiceService:
    def __init__(self):
        self.providers: Dict[str, VoiceProvider] = {
            "azure": AzureVoiceProvider(),
            "playht": PlayhtVoiceProvider(),
        }

    async def create(self, in_schema: voice_schemas.CreateVoiceSchema) -> voice_schemas.VoiceSchema:
        ...

    async def upsert(self, in_schema: voice_schemas.CreateVoiceSchema) -> voice_schemas.VoiceSchema:
        ...

    async def get_by_id(self, id: UUID) -> voice_schemas.VoiceSchema:
        ...

    async def get_by_ids(self, ids: List[UUID]) -> List[voice_schemas.VoiceSchema]:
        ...

    async def update_by_id(self, id: UUID, data: voice_schemas.UpdateVoiceSchema) -> voice_schemas.VoiceSchema:
        ...

    async def delete_by_id(self, id: UUID) -> None:
        ...

    async def paginate(self, provider: str, language: str, params: Optional[CursorParams] = None) -> CursorPage[voice_schemas.VoiceSchema]:
        p = self.providers.get(provider)
        if p is None:
            return CursorPage.create(
              total=0,
              items=[],
              params=params,
            )
      
        voices = await p.fetch_voice_list(language)
        return CursorPage.create(
            items=voices,
            total=len(voices),
            params=params,
        )
  
    async def say(self, req: voice_schemas.SayRequest) -> voice_schemas.SayResponse:
        p = self.providers.get(req.provider)
        if p is None:
            raise Exception(f"provider: {req.provider} not found")
        
        return await p.say(req)
    
    async def list_locales(self, provider: str) -> List[LocaleSchemaBase]:
        p = self.providers.get(provider)
        if p is None:
            raise HTTPException(status_code=400, detail={'error': f"provider: {provider} not found"})
    
        return await p.list_locales()
