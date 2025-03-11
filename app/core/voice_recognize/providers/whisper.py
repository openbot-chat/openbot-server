

from core.voice_recognize.voice_recognizer import VoiceRecognizer
import openai
import os
from typing import BinaryIO, Union



class Whisper(VoiceRecognizer):
    def __init__(self):
        self.model = "whisper-1"
        self.api_key = os.getenv("OPENAI_API_KEY")

    async def transcribe(self, file: Union[BinaryIO, str]) -> str:
        client = openai.AsyncOpenAI(api_key=self.api_key)

        transcript = await client.audio.transcriptions.create(
            model=self.model,
            file=file,
            response_format="json",
        )

        return transcript.text