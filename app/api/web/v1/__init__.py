from fastapi import APIRouter

from . import chat
from . import conversation
from . import voice
from . import files
from . import agent
from . import webhook


api_router = APIRouter(prefix="/web/v1", dependencies=[])


api_router.include_router(agent.router, tags=["Agent"], prefix="/agents")
api_router.include_router(chat.router, tags=["Chat"], prefix="/chat")
api_router.include_router(conversation.router, tags=["Conversation"], prefix="/conversations")
api_router.include_router(voice.router, tags=["Voice"], prefix="/voices")
api_router.include_router(files.router, tags=["File"], prefix="/files")
api_router.include_router(webhook.router, tags=["Webhook"], prefix="/webhook")