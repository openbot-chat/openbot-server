from abc import ABC, abstractmethod
from typing import BinaryIO, Union
    

    
class VoiceRecognizer(ABC):
    @abstractmethod
    async def transcribe(self, file: Union[BinaryIO, str]) -> str:
        ...