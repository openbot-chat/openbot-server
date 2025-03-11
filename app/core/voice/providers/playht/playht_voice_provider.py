import os
from typing import List, Dict, Any, Optional
from models.voice import VoiceSchema, SayRequest, SayResponse
from models.locale import LocaleSchemaBase
from ..voice_provider import VoiceProvider
import requests
import json
import logging
import asyncio
import base64
import aiohttp


PLAYHT_API = "https://play.ht/api/v2"

class PlayhtVoiceProvider(VoiceProvider):
    def __init__(self):
       self.playht_secret_key = os.getenv('PLAYHT_SECRET_KEY')
       self.playht_user_id = os.getenv('PLAYHT_USER_ID')

    def auth_headers(self):
        return {
            "Authorization": f"Bearer {self.playht_secret_key}",
            "X-USER-ID": self.playht_user_id,
        }

    async def fetch_voice_list(self, language: str = "en-US") -> List[VoiceSchema]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{PLAYHT_API}/cloned-voices", headers=self.auth_headers() | {
                "Accept": "application/json"
            }) as response:
                cloned_voices = await response.json()
                if 'error_message' in cloned_voices:
                    cloned_voices = []

                for cv in cloned_voices:
                    cv['is_cloned'] = True

            async with session.get(f"{PLAYHT_API}/voices", headers=self.auth_headers() | {
                "Accept": "application/json"
            }) as response:
                premade_voices = await  response.json()
            
        all_voices = cloned_voices + premade_voices
        voices: List[VoiceSchema] = []
        for v in all_voices:
            voices.append(VoiceSchema(
                provider="playht",
                identifier=v.get('id'),
                name=v.get('name'),
                gender=v.get('gender'),
                language=v.get('language'),
                styles=[v.get('style')] if v.get('style') else [],
                sample=v.get('sample'),
                is_cloned=v.get('is_cloned', False),
                type=v.get('type')
            ))

        return voices



    async def say(self, req: SayRequest) -> SayResponse:
        voice_response: Optional[Dict[str, Any]] = None

        output_format = req.format
        if output_format not in ["mp3", "wav", "ogg", "flac", "mulaw"]:
            output_format = "mp3"

        args = req.options or {}

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{PLAYHT_API}/tts", headers=self.auth_headers() | {
                "Accept": "text/event-stream",
                "Content-Type": "application/json"
            }, data=json.dumps({
                "text": req.text,
                "voice": req.identifier,
                "output_format": output_format,
                **args,
            })) as response:
                async for chunk in response.content.iter_any():
                    events = chunk.split(b'\r\n')
                    for event in events:
                        data: str = event.decode("utf-8")
                    
                        if not data.startswith("data: {"):
                            continue

                        data = json.loads(data[5:])
                        if "error_message" in data:
                            raise Exception(f"Play.ht: {data['error_message']}")
                    
                        logging.debug(f"Play.ht progress: [{data['stage']}] {round(data['progress'] * 100)}%")
                        if "url" in data:
                            voice_response = data
                            break
        
            if not voice_response:
                raise Exception("audio_url was None!")
  
        
            if req.format == 'base64':
                logging.debug(f"Downloading {voice_response['url']}")
          
                async with session.get(voice_response.get("url")) as response:    
                    content = await response.read()
                    return SayResponse(
                        duration=voice_response.get('duration'),
                        format="base64",
                        data=base64.b64encode(content),
                    )
            else:
                return SayResponse(
                    duration=voice_response.get('duration'),
                    format="url",
                    url=voice_response.get('url'),
                )



    async def say1(self, req: SayRequest) -> SayResponse:
        def generate_audio() -> str:
            print("xxvoice: ", req.identifier)

            r = requests.post(f"{PLAYHT_API}/tts", data=json.dumps({
                "text": req.text,
                "voice": req.identifier,
            }), headers=self.auth_headers() | {
                "Accept": "text/event-stream",
                "Content-Type": "application/json"
            }, stream=True)
            r.raise_for_status()

            for data in r.iter_lines():
                if data:
                    data: str = data.decode("utf-8")
                    if not data.startswith("data: {"):
                        continue
                    
                    data = json.loads(data[5:])
                    if "error_message" in data:
                        raise Exception(f"Play.ht: {data['error_message']}")
                    
                    logging.debug(f"Play.ht progress: [{data['stage']}] {round(data['progress'] * 100)}%")
                    if "url" in data:
                        return data
            return None

        data = await asyncio.get_event_loop().run_in_executor(None, generate_audio)
        if not data or not data['url']:
            raise Exception("audio_url was None!")
  
        print('data1: ', data)
        if req.format == 'base64':
          logging.debug(f"Downloading {data['url']}")
          data2 = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.get(data['url']))
          # print('data.content: ', data2.content)
          # io.BytesIO(data.content)
          return SayResponse(
              duration=data.get('duration'),
              format="base64",
              data=base64.b64encode(data2.content),
          )
      
        return SayResponse(
            duration=data.get('duration'),
            format="url",
            url=data.get('url'),
        )

    async def list_locales(self) -> List[LocaleSchemaBase]:
        return []