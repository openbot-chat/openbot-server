from models.agent_tool import AgentToolSchema
from .agent_tool_loader import AgentToolLoader
from typing import List, Any
from core.monkey_patching.tool import *
from models.credentials import CredentialsSchemaBase
from models.conversation import ConversationSchema
from langchain.tools.base import BaseTool, Tool
from uuid import UUID
from pydantic import BaseModel

import openai


class DallEAPIWrapper(BaseModel):
    client: Any
    async_client: Any
    n: int = 1
    size: str = "1024x1024"
    model: str = "dall-e-3"
    separator: str = "\n"

    def run(self, query: str) -> str:
        response = self.client.images.generate(prompt=query, n=self.n, size=self.size, model=self.model)
        image_urls = self.separator.join([item.url for item in response.data])
        return image_urls if image_urls else "No image was generated"

    async def arun(self, query: str) -> str:
        response = await self.async_client.images.generate(prompt=query, n=self.n, size=self.size, model=self.model)
        image_urls = self.separator.join([item.url for item in response.data])
        return image_urls if image_urls else "No image was generated"        

class DalleAgentToolLoader(AgentToolLoader):
    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None,
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:
        client = openai.OpenAI()
        async_client= openai.AsyncOpenAI()

        wrapper = DallEAPIWrapper(
            client=client,
            async_client=async_client,
        )

        return [
            Tool(
                name=str(agent_tool.tool.id),
                description=agent_tool.description or agent_tool.tool.description or "A wrapper around OpenAI DALL-E API. Useful for when you need to generate images from a text description. Input should be an image description.",
                func=wrapper.run,
                coroutine=wrapper.arun,
              ),
          ]