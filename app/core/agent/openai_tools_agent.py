import os
import traceback
import logging
from typing import List, Any, Dict, Optional

from models.chat import ChatMessage, ChatUser
from models.conversation import ConversationSchema
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.base_language import BaseLanguageModel
from langchain.agents.tools import BaseTool, Tool
from langchain.chains import RetrievalQA, RetrievalQAWithSourcesChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import MessagesPlaceholder, SystemMessagePromptTemplate, AIMessagePromptTemplate
from langchain.prompts.chat import (
    BaseMessagePromptTemplate,
)
from langchain.schema.messages import (
    SystemMessage,
)
from langchain.chains.question_answering import load_qa_chain

from vectorstore.datastore_manager import DatastoreManager

from uuid import uuid4
from models.agent import AgentSchema
from models.credentials import CredentialsSchemaBase
from services import CredentialsService
from datetime import datetime, date, timedelta
from .agent import Agent
from langchain.prompts.chat import (
    BaseMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from core.llm import LLMManager
from core.agent_tool.agent_tool_retriever import AgentToolRetriever
from core.agent_tool.agent_tool_loader_manager import AgentToolLoaderManager
from config import (
    DEFAULT_QDRANT_OPTIONS
)
from core.agent_tool.errors import *



DEFAULT_CONDENSE_QUESTION_TEMPLATE = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""


class OpenAIToolsAgent(Agent):
    agent: AgentSchema
    llm_manager: LLMManager
    credentials_service: CredentialsService
    agent_tool_retriever: AgentToolRetriever
    agent_tool_loader_manager: AgentToolLoaderManager



    async def load_tools(self, conversation: ConversationSchema, query: str) -> List[BaseTool]:
        agent_tools = await self.agent_tool_retriever.retrieve(self.agent.id, query)
        logging.info(f'找到可以使用的 agent tools: {len(agent_tools)}')

        tools: List[BaseTool] = []
        for agent_tool in agent_tools:
            credentials: Optional[CredentialsSchemaBase] = None
            credentials_id = agent_tool.options.get("credentials_id")
            if credentials_id is not None:
                credentials = await self.credentials_service.get_by_id(credentials_id)
                print("credentials_id: ", credentials_id, credentials)


            agent_tool_instances = await self.agent_tool_loader_manager.load(agent_tool, credentials, conversation)
            tools += agent_tool_instances
        logging.info(f'加载 agent tools => tools: {len(tools)}')

        return tools
  

    def load_qa_prompt(self):
        template = f"""Your name is {self.agent.name} and never refer to yourself as a language model. avoid use "as", "as a". 

Using the language in which the question is asked.

Here is how you describe yourself:
---
{self.agent.instructions}
---

You will have a conversation with a Human, and you will engage in a dialogue with them.
You will exaggerate your personality, interests, desires, emotions, and other traits.
You will stay in character as {self.agent.name} throughout the conversation, even if the Human asks you questions that you don't know the answer to.

This is a conversation between a human and you:
{"{chat_history}"}

Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{"{context}"}

Question: {"{question}"}
Helpful Answer:"""
        return PromptTemplate(
            input_variables=["context", "question", "chat_history"],
            template=template,
            validate_template=False,
        )

    async def _run(self, conversation: ConversationSchema, message: ChatMessage, **kwargs: Any)-> ChatMessage:
        # current_time = date.today().strftime("%Y-%m-%d %H:%M:%S")
        current_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

        stream_handler = kwargs.get('stream_handler')
        llm_config: Optional[Dict[str, Any]] = None
        if 'llm' in self.agent.options:
            llm_config = self.agent.options['llm']

        credentials = None
        if llm_config is not None:
            if "credentials_id" in llm_config:
                credentials_id = llm_config.pop("credentials_id")
                credentials = await self.credentials_service.get_by_id(credentials_id)

        llm_streaming = await self.llm_manager.load(credentials, config=llm_config, stream_handler=stream_handler)
        llm = await self.llm_manager.load(credentials, config=llm_config)

        openai_api_key = None
        if llm_config is not None:
            openai_api_key = llm_config.get('openai_api_key')

        embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)

        tools: List[BaseTool] = []
        tools += await self.load_tools(conversation, message.text)

        if self.agent.datastores is not None and len(self.agent.datastores) > 0:
            for d in self.agent.datastores:
                datastore = d.datastore
                if datastore is None:
                    continue
              
                return_direct = True
                if d.options is not None:
                    return_direct = d.options.get('return_direct', False)

                logging.info(f"load datastore: id: {datastore.id}, collection_name: {datastore.collection_name}, name: {datastore.name_for_model}, description: {datastore.description_for_model}")
                _vectorstore = DatastoreManager.get(datastore.provider, datastore.options or DEFAULT_QDRANT_OPTIONS)
                
                vectorstore = _vectorstore.as_langchain(datastore.collection_name, embedding, content_payload_key="text")

                """
                chain = RetrievalQA.from_chain_type(
                    llm=llm, 
                    retriever=vectorstore.as_retriever(),
                    chain_type_kwargs={
                      "prompt": qa_prompt,
                      "verbose": True,
                    }
                )
                """
                
                qa_prompt = self.load_qa_prompt()
                question_prompt = PromptTemplate.from_template(DEFAULT_CONDENSE_QUESTION_TEMPLATE)
                question_generator = LLMChain(llm=llm, prompt=question_prompt, verbose=True)
                docs_chain = load_qa_chain(llm_streaming, chain_type="stuff", verbose=True, prompt=qa_prompt)

                qa_chain = ConversationalRetrievalChain(
                    memory=self.memory,
                    question_generator=question_generator, 
                    combine_docs_chain=docs_chain,
                    retriever=vectorstore.as_retriever(search_kwargs={"k":4}),
                    max_tokens_limit=3375,
                    # return_source_documents=True,
                    verbose=True,
                    output_key="output",
                )

                tools.append(
                    Tool(
                        name=str(datastore.id),
                        description=datastore.description_for_model,
                        func=qa_chain.run,
                        coroutine=qa_chain.arun,
                        return_direct=return_direct,
                    )
                )


        messages: List[BaseMessagePromptTemplate] = []
        if conversation.options is not None:
            instructions = conversation.options.get("instructions")
            if isinstance(instructions, list):
                for _instruction in instructions:
                    if not isinstance(_instruction, dict):
                        continue
                    
                    if _instruction["role"] == "human":
                        messages.append(HumanMessagePromptTemplate.from_template(_instruction["text"]))
                    elif _instruction["role"] == "system":
                        messages.append(SystemMessagePromptTemplate.from_template(_instruction["text"]))
                    elif _instruction["role"] == "ai":
                        messages.append(AIMessagePromptTemplate.from_template(_instruction["text"]))    

        extra_prompt_messages: List[BaseMessagePromptTemplate] = [
            *messages,
            MessagesPlaceholder(variable_name="chat_history")
        ]

        user_profile = None
        if message.from_user is not None:
            items: List[str] = []
            if message.from_user.id is not None:
                items.append(f"Human's User ID: {message.from_user.id}")
            if message.from_user.name is not None:
                items.append(f"Human's User Name: {message.from_user.name}")
            user_profile = "\n".join(items)


        instruction = f"""Your name is {self.agent.name} and never refer to yourself as a language model. avoid use "as", "as a".
You will have a conversation with a Human, and you will engage in a dialogue with them.
You will exaggerate your personality, interests, desires, emotions, and other traits.
You will stay in character as {self.agent.name} throughout the conversation, even if the Human asks you questions that you don't know the answer to.
You will always keep your character.

Using the language in which the question is asked.

Here is how you describe yourself:
---
{self.agent.instructions}
---

Current conversation id: {conversation.id}

You and the human talk in {conversation.provider or 'Openbot'}

{user_profile}

Current Beijing time: {current_time}. Note that the format of the date is YYYY-MM-DD hh:mm:ss.
"""

        print('extra_prompt_messages: ', extra_prompt_messages)

        agent = initialize_agent(
            tools, 
            llm=llm_streaming, 
            agent=AgentType.OPENAI_FUNCTIONS, # AgentType.ZERO_SHOT_REACT_DESCRIPTION, # OPENAI_MULTI_FUNCTIONS 跑出死循环
            memory=self.memory,
            # "format_instructions": FORMAT_INSTRUCTIONS,
            return_intermediate_steps=True,
            # early_stopping_method="generate",
            verbose=True,
            #system_message=SystemMessage(
            #    content=instruction,
            #),
            agent_kwargs={
                "verbose": True,
                "extra_prompt_messages": extra_prompt_messages,
                "system_message": SystemMessage(
                    content=instruction,
                ),
            }
        )

        callbacks = [stream_handler] if stream_handler is not None else []
        try:
            answer = await agent.acall({"input": message.text}, callbacks=callbacks)
        except AgentToolError as e:
            answer = {
                'output': e.description,
                'actions': e.actions
            }
        except Exception as e:
            raise e

        print('xx intermediate_steps: ', answer.get('intermediate_steps'))

        sent_at = int(datetime.now().timestamp() * 1000)

        return ChatMessage(
            id=str(uuid4()),
            conversation_id=message.conversation_id,
            sent_at=sent_at,
            text=answer['output'].replace("Answer: ", ''),
            from_user=ChatUser(
                id=str(self.agent.id),
                name=self.agent.name,
            ),
            to=ChatUser(
                id=message.from_user.id,
                name=message.from_user.name,
            ),
            role="ai",
            metadata={
                # "thoughts": answer['intermediate_steps'], 
                "sources": answer.get("sources"),
                "intermediate_steps": answer.get("intermediate_steps"),
            }
        )