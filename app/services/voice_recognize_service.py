from fastapi import HTTPException
from typing import Dict, BinaryIO, Union
from core.voice_recognize import VoiceRecognizer
from core.voice_recognize.providers.whisper import Whisper 



class VoiceRecognizeService:
    def __init__(self):
        self.providers: Dict[str, VoiceRecognizer] = {
            "whisper": Whisper(),
        }
  
    async def transcribe(self, provider: str, file: Union[BinaryIO, str]) -> str:
        p = self.providers.get(provider)
        if p is None:
            raise HTTPException(status_code=400, detail={ 'error': f'recognize provider: {provider} not found' })
      
        return await p.transcribe(file)
