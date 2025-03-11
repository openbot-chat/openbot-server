
from fastapi import APIRouter
from models.api import VideoGenerationRequest

import requests

router = APIRouter()


@router.post('')
def create(
  req: VideoGenerationRequest
):
  response = requests.post(
    'https://api.d-id.com/talks',
    
    headers={
      "Authorization": "Basic YWxhbkBieXRlcnVzaC5jbw:58KX3IjHoieIVIsNeuVa3",
      "Accept": "application/json",
      "content-type": "application/json" 
    },
    json={
      "script": {
        "type": "text",
        "provider": {
          "type": "microsoft",
          "voice_id": "zh-CN-YunyeNeural"
        },
        "ssml": "false",
        "input": req.prompt,
      },
      "config": {
        "fluent": "false",
        "pad_audio": "0.0"
      },
      "source_url": req.source_url,
    }
  )

  return response.json()

@router.get('/{id}')
def get_by_id(id: str):
  response = requests.get(
    f'https://api.d-id.com/talks/{id}',
    headers={
      "Authorization": "Basic YWxhbkBieXRlcnVzaC5jbw:58KX3IjHoieIVIsNeuVa3",
      "Accept": "application/json",
      "content-type": "application/json" 
    }
  )
  return response.json()