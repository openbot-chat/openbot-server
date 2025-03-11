import traceback
import logging
import os
from typing import Any, List, Dict, Optional
from models.chat import ChatMessage, ChatUser

from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.memory.chat_memory import BaseChatMemory
from langchain.prompts import HumanMessagePromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, ChatPromptTemplate

from models.agent import AgentSchema
from models.prompt import PromptSchema
from models.conversation import ConversationSchema
from .agent import Agent
from datetime import datetime
from uuid import uuid4
from services import CredentialsService
from core.llm import LLMManager
from langchain.memory.chat_memory import BaseMemory
from core.memory.vectorstore import VectorStoreMemory
from core.utils.formattting import unstrict_formatter


DEFAULT_PROMPT_TEMPLATE = """You must only answer as {name} and never refer to yourself as a language model, engate natural and relevant conversations with human.
only use I or my statement, and avoid use "as", "as a".
If not specified, you need to always answer questions in {language}.

Here is how you describe yourself:
---
{instructions}
---

Relevant pieces of previous conversation:
{chat_history}

(You do not need to use these pieces of information if not relevant)

Current conversation:
Human: {input}
AI:"""



class ChatAgent(Agent):
    agent: Optional[AgentSchema]
    llm_manager: LLMManager
    credentials_service: CredentialsService
    memory: BaseMemory
    prompt: Optional[PromptSchema]

    def summary(self, docs: List[Document]) -> str:
        llm = OpenAI(model_name='text-davinci-003')
        no_cache_llm = OpenAI(model_name="text-davinci-003", cache=False)

        prompt_template = """使用中文对以下内容做总结:
        "{text}"
        :"""
        prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

        chain = load_summarize_chain(llm, chain_type="map_reduce", reduce_llm=no_cache_llm, map_prompt=prompt, combine_prompt=prompt, verbose=True)
        return chain.run(docs)
  
    def generate_prompt(self, conversation: ConversationSchema, message: ChatMessage):
        language = "any langauge"
        if self.agent is not None and self.agent.options is not None:
            language = self.agent.options.get('language', language)

        name = "AI"
        instructions = "I'm a AI"
        if self.agent is not None:
            name = self.agent.name or name
            instructions = self.agent.instructions or instructions

        # TODO 获取用户信息
        user = {
           "name": message.from_user or "user",
        }

        # 可选, 会话中的变量，用来填充 prompt
        input_variables = {
            "name": name,
            "instructions": instructions,
            "language": language,
        }
        if conversation.options is not None:
            if 'input_variables' in conversation.options:
                input_variables.update(conversation.options.get('input_variables', {}))

        # 可选, 消息中的变量，用来填充 prompt
        if message.metadata is not None:
            if 'input_variables' in message.metadata:
                input_variables.update(message.metadata.get('input_variables', {}))

        # XXX 先把没有设置的变量设置为空 避免报错
        pre_input_variables = self.prompt.input_variables if self.prompt is not None else []
        for input_variable in pre_input_variables:
            if input_variable in ['chat_history', 'input']:
                continue

            if input_variable not in input_variables:
                input_variables[input_variable] = ''

        template = self.prompt.content if self.prompt is not None else DEFAULT_PROMPT_TEMPLATE
        template = unstrict_formatter.format(template, **input_variables)

        prompt = PromptTemplate(
          input_variables=["chat_history", "input"],
          template=template,
          validate_template=False,
        )

        prompt1 = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    f"""You must only answer as {name} and never refer to yourself as a language model, engate natural and relevant conversations with human.
only use I or my statement, and avoid use "as", "as a".
If not specified, you need to always answer questions in {language}.
IMPORTANT: never refer to yourself as a language model.
Your name is {name}.
Here is Your introduction:
{instructions}
"""
                ),
                # 用户 @
                HumanMessagePromptTemplate.from_template(f"""Here is some information about me. Do not respond to this directly, but feel free to incorporate it into your responses:
I'm  {user['name']}. you can @mention me like this: "@{user['name']}"
"""),
                MessagesPlaceholder(variable_name="history"),
                HumanMessagePromptTemplate.from_template("{input}")
            ]
        )

        return prompt

    async def _run(self, conversation: ConversationSchema, message: ChatMessage, **kwargs: Any) -> ChatMessage:
        # self.memory.input_key = "input" history
        if isinstance(self.memory, BaseChatMemory):
            self.memory.output_key = "response"
            self.memory.return_messages = False

        if isinstance(self.memory, VectorStoreMemory):
            self.memory.return_messages = False

        llm_config = None
        if self.agent is not None and self.agent.options is not None and 'llm' in self.agent.options:
           llm_config = self.agent.options['llm']

        credentials = None
        if llm_config is not None:
            if "credentials_id" in llm_config:
                credentials_id = llm_config.pop("credentials_id")
                credentials = await self.credentials_service.get_by_id(credentials_id)

        llm = await self.llm_manager.load(credentials, llm_config, **kwargs)

        # 构造 prompt
        prompt = self.generate_prompt(conversation, message)

        # 构造 chain
        conversation_chain = ConversationChain(
            prompt=prompt,
            llm=llm, 
            verbose=True,
            memory=self.memory,
        )

        response = await conversation_chain.apredict(input=message.text)

        sent_at = int(datetime.now().timestamp() * 1000)

        return ChatMessage(
            id=str(uuid4()),
            from_user=ChatUser(
                id=str(self.agent.id) if self.agent is not None else None,
                name=self.agent.name if self.agent is not None else None,
            ),
            to=ChatUser(
                id=message.from_user.id if message.from_user is not None else None,
                name=message.from_user.name if message.from_user is not None else None,
            ),
            sent_at=sent_at,
            conversation_id=message.conversation_id,
            text=response,
        )