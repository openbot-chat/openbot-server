from typing import Any
from models.agent import AgentSchema
from .qa_agent import QAAgent
from services.prompt_service import PromptService
from services.conversation_service import ConversationService
from services.prompt_service import PromptService
from core.llm.manager import LLMManager
from .agent import Agent

from langchain.memory.chat_memory import BaseMemory


class QAAgentBuilder:
    async def build(
        self, 
        agent: AgentSchema,
        prompt_service: PromptService,
        **kwargs: Any,
    ) -> Agent:
        qa_prompt_id = None
        question_prompt_id = None
        if agent.options is not None:
            if 'chain' in agent.options:
                chain_options = agent.options.get('chain')
                if 'qa' in chain_options:
                    qa_options = chain_options.get('qa')
                    question_prompt_id = qa_options.get('question_prompt_id')
                    qa_prompt_id = qa_options.get('qa_prompt_id')

        qa_prompt = None
        question_prompt = None

        """
        # 用会话中的 prompt 覆盖
        if conversation.options is not None:
            qa_prompt_id = conversation.options.get('qa_prompt_id', qa_prompt_id)
        """
        if question_prompt_id is not None:
            question_prompt = await prompt_service.get_by_id(question_prompt_id)

        if qa_prompt_id is not None:
            qa_prompt = await prompt_service.get_by_id(qa_prompt_id)
        
        return QAAgent(
            agent=agent,
            question_prompt=question_prompt,
            qa_prompt=qa_prompt,
            **kwargs,
        )