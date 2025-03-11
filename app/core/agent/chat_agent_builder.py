from typing import Any
from models.agent import AgentSchema
from models.conversation import ConversationSchema
from .chat_agent import ChatAgent
from services.prompt_service import PromptService
from services.conversation_service import ConversationService
from services.credentials_service import CredentialsService
from core.llm.manager import LLMManager
from .agent import Agent

from langchain.memory.chat_memory import BaseMemory


class ChatAgentBuilder:
    async def build(
        self, 
        agent: AgentSchema,
        prompt_service: PromptService,
        conversation_service: ConversationService,
        credentials_service: CredentialsService,
        llm_manager: LLMManager,
        memory: BaseMemory,
        **kwargs: Any,
    ) -> Agent:
        prompt_id = None
        if agent.options is not None:
            if 'chain' in agent.options:
                chain_options = agent.options.get('chain')
                if 'chat' in chain_options:
                    chat_options = chain_options.get('chat')
                    prompt_id = chat_options.get('prompt_id')

        prompt = None

        """
        # 用会话中的 prompt 覆盖
        if conversation.options is not None:
            prompt_id = conversation.options.get('prompt_id', prompt_id)
        """
        if prompt_id is not None:
            prompt = await prompt_service.get_by_id(prompt_id)
    
        return ChatAgent(
            agent=agent,
            prompt=prompt,
            memory=memory,
            llm_manager=llm_manager,
            credentials_service=credentials_service,
            conversation_service=conversation_service,
        )