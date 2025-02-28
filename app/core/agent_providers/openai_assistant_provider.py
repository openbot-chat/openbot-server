from .agent_provider import AgentProvider
from typing import Dict, Any
import openai
from models.agent import AgentSchema



class OpenAIAssistantProvider(AgentProvider):
    async def create(self, agent: AgentSchema, options: Dict[str, Any]):
        api_key = options.get('api_key', None)
        organization = options.get('organization', None)

        client = openai.AsyncOpenAI(api_key=api_key, organization=organization)
        assistant = await client.beta.assistants.create(
            name=agent.name,
            instructions=agent.instructions,
            description=agent.description,
            tools=[{"type": "code_interpreter"}],
            model="gpt-4-1106-preview",
        )
        
        print('为给定agent创建 gpt assistant: ', assistant)

        return assistant.dict()
    
    async def delete(self, id: str, options: Dict[str, Any]) -> Any:
        api_key = options.get('api_key', None)
        organization = options.get('organization', None)

        client = openai.AsyncOpenAI(api_key=api_key, organization=organization)
        r = await client.beta.assistants.delete(id)
        return r.dict()

    async def update(self, id: str, options: Dict[str, Any], updates: Dict[str, Any]) -> Any:
        api_key = options.get('api_key', None)
        organization = options.get('organization', None)

        client = openai.AsyncOpenAI(api_key=api_key, organization=organization)
        assitant = await client.beta.assistants.update(
            assistant_id=id,
            **updates,
        )
        return assitant.dict()