from abc import ABC, abstractmethod
from typing import List
from models.voice import VoiceSchema, SayRequest, SayResponse
from models.locale import LocaleSchemaBase


class VoiceProvider(ABC):
    @abstractmethod
    async def fetch_voice_list(self, language: str) -> List[VoiceSchema]:
        ...
  
    @abstractmethod
    async def say(self, req: SayRequest) -> SayResponse:
       ...
    
    @abstractmethod
    async def list_locales(self) -> List[LocaleSchemaBase]:
        ...