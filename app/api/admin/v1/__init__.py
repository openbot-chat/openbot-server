from fastapi import APIRouter

from . import user
from . import org
from . import custom_plan
from . import account
from . import agent
from . import files
from . import chat
from . import conversation
from . import datastore
from . import datasource
from . import document
from . import image
from . import voice
from . import avatar
from . import video
from . import prompt
from . import integration
from . import tool
from . import toolkit
from . import api_key
from . import chain
from . import prediction
from . import marketplace
from . import subscription

from . import credentials
from . import connection_provider
from . import app


api_router = APIRouter(prefix="/admin/v1", dependencies=[])

api_router.include_router(org.router, tags=["Org"], prefix="/orgs")
api_router.include_router(user.router, tags=["User"], prefix="/users")
api_router.include_router(account.router, tags=["Account"], prefix="/accounts")

api_router.include_router(custom_plan.router, tags=["CustomPlan"], prefix="/custom-plans")


api_router.include_router(files.router, tags=["File"], prefix="/files")
api_router.include_router(agent.router, tags=["Agent"], prefix="/agents")
api_router.include_router(chain.router, tags=["Chain"], prefix="/chains")
api_router.include_router(chat.router, tags=["Chat"], prefix="/chat")
api_router.include_router(conversation.router, tags=["Conversation"], prefix="/conversations")
api_router.include_router(datastore.router, tags=["Datastore"], prefix="/datastores")
api_router.include_router(datasource.router, tags=["Datasource"], prefix="/datasources")
api_router.include_router(document.router, tags=["Document"], prefix="/documents")
api_router.include_router(image.router, tags=["Image"], prefix="/images")
api_router.include_router(avatar.router, tags=["Avatar"], prefix="/avatars")
api_router.include_router(voice.router, tags=["Voice"], prefix="/voices")
api_router.include_router(video.router, tags=["Video"], prefix="/video")
api_router.include_router(prompt.router, tags=["Prompt"], prefix="/prompts")
api_router.include_router(tool.router, tags=["Tool"], prefix="/tools")
api_router.include_router(toolkit.router, tags=["Toolkit"], prefix="/toolkits")
api_router.include_router(integration.router, tags=["Integration"], prefix="/integrations")
api_router.include_router(api_key.router, tags=["ApiKey"], prefix="/apikeys")
api_router.include_router(prediction.router, tags=["Prediction"], prefix="/predictions")

api_router.include_router(credentials.router, tags=["Credentials"], prefix="/credentials")
api_router.include_router(connection_provider.router, tags=["Connections"], prefix="/connection-providers")
api_router.include_router(app.router, tags=["Apps"], prefix="/apps")

# api_router.include_router(category.router, tags=["Category"], prefix="/categories")
api_router.include_router(marketplace.router, tags=["Marketplace"], prefix="/marketplace")
api_router.include_router(subscription.router, tags=["Subscription"], prefix="/subscription")
