from typing import Optional, List
from fastapi import APIRouter, Depends, Request, Query, UploadFile, Form
from services.voice_service import VoiceService
from services.voice_recognize_service import VoiceRecognizeService

from models.voice import VoiceSchema, CreateVoiceSchema, UpdateVoiceSchema, SayRequest, SayResponse, TranscribeResponse
from models.locale import LocaleSchemaBase
from uuid import UUID
from schemas.pagination import CursorPage, CursorParams

router = APIRouter()


@router.get("/{voice_id}", status_code=201, response_model=VoiceSchema)
async def get_a_voice(
    request: Request,
    voice_id: UUID,
    voice_service: VoiceService = Depends(VoiceService),
):  
    return await voice_service.get_by_id(voice_id)



@router.post("", status_code=201, response_model=VoiceSchema)
async def create_a_voice(
    request: Request,
    data: CreateVoiceSchema,
    voice_service: VoiceService = Depends(VoiceService),
):
    voice = await voice_service.create(data)
    return voice

@router.patch("/{voice_id}", response_model=VoiceSchema)
async def update_a_voice(
    request: Request,
    voice_id: UUID,
    data: UpdateVoiceSchema,
    voice_service: VoiceService = Depends(VoiceService),
):
    return await voice_service.update_by_id(voice_id, data)

@router.get("", response_model=CursorPage[VoiceSchema], response_model_exclude_unset=True, response_model_exclude_none=True)
async def list(
    request: Request,
    params: CursorParams = Depends(),
    provider: str = Query(None),
    language: str = Query(default="en-US"),
    voice_service: VoiceService = Depends(VoiceService),
):
    return  await voice_service.paginate(provider, language, params)

@router.post("/say", response_model=SayResponse, response_model_exclude_unset=True, response_model_exclude_none=True)
async def say(
    req: SayRequest,
    voice_service: VoiceService = Depends(VoiceService)
):
    return await voice_service.say(req)


from aiofiles import tempfile
from pathlib import Path


async def iter_chunks(file, chunk_size):
   while chunk := await file.read(chunk_size):
      yield chunk


@router.post('/transcribe', response_model=TranscribeResponse)
async def transcribe(
    file: UploadFile,
    provider: str = Form("whisper"),
    prompt: Optional[str] = Form(None),
    voice_recognize_service: VoiceRecognizeService = Depends(VoiceRecognizeService)
):
    try:
        text = None
        suffix = Path(file.filename).suffix
        async with tempfile.NamedTemporaryFile(delete=True, suffix=suffix) as tmp_file:
            async for chunk in iter_chunks(file, chunk_size=4096):
                await tmp_file.write(chunk)
            await tmp_file.flush()

            sync_temp_file = open(tmp_file.name, mode='rb')
            # sync_temp_file.seek(0)
            text = await voice_recognize_service.transcribe(provider, sync_temp_file)
        return TranscribeResponse(text=text)
    finally:
        file.file.close()


@router.get("/locales", response_model=List[LocaleSchemaBase], response_model_exclude_unset=True, response_model_exclude_none=True)
async def list_locales(
    request: Request,
    provider: str = Query(None),
    voice_service: VoiceService = Depends(VoiceService),
):
    return await voice_service.list_locales(provider)
