import os
import traceback
import logging
from typing import List, Any, Dict, Optional

from models.chat import ChatMessage, ChatUser
from models.conversation import ConversationSchema

from langchain.agents import initialize_agent, load_tools
from langchain.agents.agent_types import AgentType

from langchain.tools.vectorstore.tool import VectorStoreQATool, VectorStoreQAWithSourcesTool
from langchain.base_language import BaseLanguageModel
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.llms.loading import load_llm_from_config

from langchain.chains import LLMChain, RetrievalQAWithSourcesChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferWindowMemory, RedisChatMessageHistory
from langchain.prompts import HumanMessagePromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, ChatPromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain.agents.agent_toolkits import NLAToolkit
from langchain.tools.plugin import AIPlugin
from uuid import uuid4, UUID
from models.agent import AgentSchema
import openai

from services import CredentialsService
from datetime import datetime
from .agent import Agent
from langchain.requests import Requests
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
)
import json
from vectorstore import DatastoreManager
from config import (
   DEFAULT_QDRANT_OPTIONS
)


class MyVectorStoreQAWithSourcesTool(VectorStoreQAWithSourcesTool):
    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        chain = RetrievalQAWithSourcesChain.from_chain_type(
            self.llm, retriever=self.vectorstore.as_retriever()
        )
        
        result = await chain.acall({chain.question_key: query}, return_only_outputs=True)
        return json.dumps(result)


def get_llm(config: Dict, **kwargs: Any):
    llm = None
    if config is not None:
        try:
            llm = load_llm_from_config(config.copy())
        except Exception as e:
            print('load llm error', e)       
            llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, verbose=True)
    else:
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, verbose=True)

    stream_handler = kwargs.get('stream_handler')
    if stream_handler is not None:
        llm.streaming = True
        llm.callbacks = [stream_handler]

    print('llm: ', llm)

    return llm



class ToolsAgent(Agent):
    def __init__(
        self, agent: AgentSchema, 
        credentials_service: CredentialsService,
        **kwargs: Any
    ):
        self.agent = agent
        self.vectorstore = DatastoreManager.get('qdrant', DEFAULT_QDRANT_OPTIONS)
        self.credentials_service = credentials_service

    async def _run(self, conversation: ConversationSchema, message: ChatMessage, **kwargs: Any)-> ChatMessage:
        url = os.getenv("REDIS_URL")
        # 先将就用
        chat_history = RedisChatMessageHistory(url=url, ttl=600, session_id=message.conversation_id)

        memory = ConversationBufferWindowMemory(
            memory_key="chat_history", 
            return_messages=True,
            chat_memory=chat_history,
        )


        stream_handler = kwargs.get('stream_handler')
        llm_config = None
        if 'llm' in self.agent.options:
           llm_config = self.agent.options['llm']

        llm = get_llm(llm_config, stream_handler=stream_handler)
        
        openai_api_key = None
        if llm_config is not None:
           openai_api_key = llm_config.get('openai_api_key')

        embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)

        tools = []

        ### load built-in tools if needed
        tools += load_tools(['serpapi'], llm)

        if self.agent.datastores is not None and len(self.agent.datastores) > 0:
          for d in self.agent.datastores:
            datastore = d.datastore
            if datastore is None:
               continue
          
            return_direct = True
            if d.options is not None:
               return_direct = d.options.get('return_direct', True)

            logging.info(f"load datastore: id: {datastore.id}, name: {datastore.name_for_model}, description: {datastore.description_for_model}")
            vectorstore = self.vectorstore.as_langchain(datastore.collection_name, embedding, content_payload_key="text")

            tools.append(
              # VectorStoreQATool
              MyVectorStoreQAWithSourcesTool(
                  name=datastore.name_for_model, 
                  description=datastore.description_for_model,
                  vectorstore=vectorstore,
                  llm=llm,
                  verbose=True,
                  return_direct=return_direct,
                  # memory=message_history,
              )
            )

        agent = initialize_agent(
            tools, 
            llm=llm, 
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            # "format_instructions": FORMAT_INSTRUCTIONS,
            # return_intermediate_steps=True,
            early_stopping_method="generate",
            verbose=True
        )

        try:
            answer = await agent.acall({"input": message.text})
            # answer = await asyncify(agent)({"input": message.text})

            """
            action = answer['intermediate_steps']
            sources = ''
            for a, data in action:
                sources = a.tool
                break
            """
            print('answer: ', answer)
        except Exception as e:
            print(traceback.format_exc())
            chat_history.clear()
            answer = await agent.acall({"input": message.text})
            # answer = await asyncify(agent)({"input": message.text})

        sent_at = int(datetime.now().timestamp() * 1000)

        return ChatMessage(
            id=str(uuid4()),
            conversation_id=message.conversation_id,
            sent_at=sent_at,
            text=answer['output'].replace("Answer: ", ''),
            from_user=ChatUser(
                id=self.agent.id,
                name=self.agent.name,
            ),
            to=ChatUser(
                id=message.from_user.id,
                name=message.from_user.name,
            ),
            metadata={
                # "thoughts": answer['intermediate_steps'], 
                "sources": answer.get("sources"), 
            }
        )

    def generate_questions(answer: str) -> str:
        followupQaPromptTemplate = """Generate three very brief follow-up questions from the answer {answer} that the user would likely ask next.
        Use double angle brackets to reference the questions, e.g. <Is there a more details on that?>.
        Try not to repeat questions that have already been asked.
        Only generate questions and do not generate any text before or after the questions, such as 'Next Questions'"""

        finalPrompt = followupQaPromptTemplate.format(answer = answer['output'])

        try:
            completion = openai.Completion.create(
                engine='text-davinci-003',
                prompt=finalPrompt,
                temperature=0.3,
                max_tokens=3000,
                n=1
            )
            nextQuestions = completion.choices[0].text
        except Exception as e:
            logging.error(e)
            nextQuestions = ''

        return nextQuestions