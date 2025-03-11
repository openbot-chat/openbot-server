import logging
from typing import List, Any, Dict, Optional

from models.chat import ChatMessage, ChatUser
from models.conversation import ConversationSchema
from langchain.agents.tools import BaseTool
from uuid import uuid4
from models.agent import AgentSchema
from models.credentials import CredentialsSchemaBase
from models.conversation import UpdateConversationSchema
from models.agent_tool import *
from services import CredentialsService
from datetime import datetime, timedelta
from .agent import Agent
from core.llm import LLMManager
from core.agent_tool.agent_tool_retriever import AgentToolRetriever
from core.agent_tool.agent_tool_loader_manager import AgentToolLoaderManager
from core.agent_tool.errors import *
import openai
from ext.langchain.agents.openai_assistant.base import AsyncOpenAIAssistantRunnable
from langchain.agents import AgentExecutor




class OpenAIAssistantAgent(Agent):
    agent: AgentSchema
    llm_manager: LLMManager
    credentials_service: CredentialsService
    agent_tool_retriever: AgentToolRetriever
    agent_tool_loader_manager: AgentToolLoaderManager

    async def load_tools(self, conversation: ConversationSchema, query: str) -> List[BaseTool]:
        # 找 datastore 并转化成 tool
 
        logging.debug(f'找到可以使用的 agent datastores: ', self.agent.datastores)
        agent_datastores = self.agent.datastores or []

        agent_datastore_tools: List[AgentToolSchema] = []

        # 把 datastore 转换成 datastore tool
        for agent_datastore in agent_datastores:
            datastore = agent_datastore.datastore
            if not datastore:
                continue
            
            agent_tool = AgentToolSchema(
                id=agent_datastore.id,
                tool_id=datastore.id,
                agent_id=self.agent.id,
                name=datastore.name_for_model,
                description=datastore.description_for_model,
                tool=ToolSchema(
                    id=datastore.id,
                    name=datastore.name_for_model,
                    description=datastore.description_for_model,
                    created_at=datastore.created_at,
                    updated_at=datastore.updated_at,
                    type='datastore',
                    options={},
                ),
                options={
                    "datastore_id": str(datastore.id),
                    "max_results": 4,
                    # "score_threshold": 0.5,
                },
                created_at=agent_datastore.created_at,
                updated_at=agent_datastore.updated_at,
            )

            agent_datastore_tools.append(agent_tool)
        logging.info(f'找到可以使用的 agent datastore tools: {len(agent_datastore_tools)}')


        agent_tools = await self.agent_tool_retriever.retrieve(self.agent.id, query)

        agent_tools.extend(agent_datastore_tools)

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
  
    async def _run(self, conversation: ConversationSchema, message: ChatMessage, **kwargs: Any)-> ChatMessage:
        # current_time = date.today().strftime("%Y-%m-%d %H:%M:%S")
        current_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

        stream_handler = kwargs.get('stream_handler')
        
        tools: List[BaseTool] = []
        tools += await self.load_tools(conversation, message.text)

        user_profile = None
        if message.from_user is not None:
            items: List[str] = []
            if message.from_user.id is not None:
                items.append(f"Human's User ID: {message.from_user.id}")
            if message.from_user.name is not None:
                items.append(f"Human's User Name: {message.from_user.name}")
            user_profile = "\n".join(items)


        instructions = f"""Your name is {self.agent.name} and never refer to yourself as a language model. avoid use "as", "as a".
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

        """
        assistant_message = await client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message.text,
        )


        try:
            run = await client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
                instructions=instructions,
            )
            # TODO check run status == 'completed'
            # TODO list thread messages, fetch messages added by ai
        except AgentToolError as e:
            answer = {
                'output': e.description,
                'actions': e.actions
            }
        except Exception as e:
            raise e
        """

        agent_options = self.agent.options or {}
        provider_options = agent_options.get('openai_assistant', {})
        assistant_id = str(provider_options['id'])
        api_key = provider_options.get('api_key')
        organization = provider_options.get('organization')
        model = provider_options.get('api_key', 'gpt-4-1106-preview')        

        client = openai.AsyncOpenAI(api_key=api_key, organization=organization)

        # ensure thread            
        thread_id = (conversation.options or {}).get('thread_id', None)
        if thread_id is None:
            thread = await client.beta.threads.create()
            
            new_options = (conversation.options or {}).copy()
            new_options['thread_id'] = thread.id
            print(f'openai assistant thread {thread.id} created')
            await self.conversation_service.update_by_id(conversation.id, UpdateConversationSchema(options=new_options))
            thread_id = thread.id

        agent = AsyncOpenAIAssistantRunnable(
            client=client,
            assistant_id=assistant_id,
            as_agent=True,
        )

        agent_executor = AgentExecutor(agent=agent, tools=tools)

        try:
            answer = await agent_executor.ainvoke({"content": message.text, "thread_id": thread_id, "model": model})

            # 因为目前没有流式API, 所以先手动补充一次
            if stream_handler is not None:
                await stream_handler.on_llm_new_token(answer['output'])
        except AgentToolError as e:
            answer = {
                'output': e.description,
                'actions': e.actions
            }
        except Exception as e:
            raise e

        print("answer: ", answer)

        sent_at = int(datetime.now().timestamp() * 1000)

        return ChatMessage(
            id=str(uuid4()),
            conversation_id=message.conversation_id,
            sent_at=sent_at,
            text=answer['output'],
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