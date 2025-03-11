from fastapi import FastAPI

from channels.manager import HubManager 
from chat.chat_api_handler import ChatAPIHandler
from core.memory import MemoryManager

from api.dependencies.agent_tool_loader_manager import get_agent_tool_loader_manager
from api.dependencies.get_llm_manager import get_llm_manager
from redis.asyncio import Redis, ConnectionPool
import os
import logging



def create_start_app_handler(app: FastAPI):
    async def startup() -> None:
        print('create_start_app_handler')
        url = os.getenv("REDIS_URL")
        redis_pool = ConnectionPool.from_url(url)
        app.state.redis_pool = redis_pool
        app.state.redis = Redis(connection_pool=redis_pool)

        hub_manager = HubManager()
        llm_manager = get_llm_manager()
        memory_manager = MemoryManager()
        api_handler = ChatAPIHandler(hub_manager, llm_manager, memory_manager, app.state.redis)

        
        agent_tool_loader_manager = get_agent_tool_loader_manager(llm_manager)

        app.state.agent_tool_loader_manager = agent_tool_loader_manager
        app.state.llm_manager = llm_manager
        app.state.memory_manager = memory_manager
        app.state.hub_manager = hub_manager
        app.state.api_handler = api_handler
    return startup

def create_stop_app_handler(app: FastAPI):
    async def stop_app() -> None:
        logging.info('redis: disconnecting ...')
        await app.state.redis_pool.disconnect()
        logging.info('redis: disconnected')
        print("stop_app")

    return stop_app
