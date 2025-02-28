from services.voice_recognize_service import VoiceRecognizeService
from models.chat import ChatMessage
from models.conversation import ConversationSchema
import aiohttp
from aiofiles import tempfile
from .message_routine import MessageProcessor
import logging
import os



async def download_file(url: str, temp_file_path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            with open(temp_file_path, 'wb') as file:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    file.write(chunk)

class VoiceTranscribeProcessor(MessageProcessor):
    def __init__(self, voice_recognize_service: VoiceRecognizeService):
        self.voice_recognize_service = voice_recognize_service

    async def process(
        self,
        conversation: ConversationSchema,
        message: ChatMessage,
    ):    
        voice = message.voice
        if message.text is not None and len(message.text) > 0:
            return

        if not voice:
            return

        text = None
        
        file_name = os.path.basename(voice.url)
        file_extension = os.path.splitext(file_name)[1]

        async with tempfile.NamedTemporaryFile(delete=True, suffix=file_extension) as tmp_file:
            await download_file(voice.url, str(tmp_file.name))

            sync_temp_file = open(tmp_file.name, mode='rb')
            text = await self.voice_recognize_service.transcribe("whisper", sync_temp_file)
            logging.debug(f"VoiceTranscribe transcribe Message, url: {voice.url} -> text: {text}")

        message.text = text