import os
import traceback
import logging
from typing import Any, Dict, Optional
from models.chat import ChatMessage, ChatUser
from models.agent import AgentSchema
from models.conversation import ConversationSchema

from langchain.base_language import BaseLanguageModel
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.chains.question_answering import load_qa_chain
import openai
from datetime import datetime

from .agent import Agent
from uuid import uuid4, UUID
from core.llm import LLMManager
from vectorstore.datastore_manager import DatastoreManager
from services import CredentialsService
from config import (
    DEFAULT_QDRANT_OPTIONS
)

from models.prompt import PromptSchema
from core.utils.formattting import unstrict_formatter
import pydash
from core.monkey_patching.vectorstore_retriever import *



DEFAULT_CONDENSE_QUESTION_TEMPLATE = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""



DEFAULT_QA_TEMPLATE = """Your name is {name} and never refer to yourself as a language model. avoid use "as", "as a". 

Using the language in which the question is asked.

Here is how you describe yourself:
---
{instructions}
---

You will have a conversation with a Human, and you will engage in a dialogue with them.
You will exaggerate your personality, interests, desires, emotions, and other traits.
You will stay in character as {name} throughout the conversation, even if the Human asks you questions that you don't know the answer to.

This is a conversation between a human and you:
{chat_history}

Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Helpful Answer:"""



class QAAgent(Agent):
    agent: AgentSchema
    llm_manager: LLMManager
    credentials_service: CredentialsService
    question_prompt: Optional[PromptSchema]
    qa_prompt: Optional[PromptSchema]

    def load_question_prompt(self, conversation: ConversationSchema, message: ChatMessage):
        language = "any langauge"
        if self.agent.options is not None:
            language = self.agent.options.get('language', language)

        name = self.agent.name or "AI"
        instructions = self.agent.instructions or "I'm a AI"

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
        pre_input_variables = self.qa_prompt.input_variables if self.qa_prompt is not None else []
        for input_variable in pre_input_variables:
            if input_variable in ["context", "question", "chat_history"]:
                continue

            if input_variable not in input_variables:
                input_variables[input_variable] = ''

        template = self.question_prompt.content if self.question_prompt is not None else DEFAULT_CONDENSE_QUESTION_TEMPLATE
        template = unstrict_formatter.format(template, **input_variables)

        return PromptTemplate.from_template(template)

    def generate_qa_prompt(self, conversation: ConversationSchema, message: ChatMessage):
        language = "any langauge"
        if self.agent.options is not None:
            language = self.agent.options.get('language', language)

        name = self.agent.name or "AI"
        instructions = self.agent.instructions or "I'm a AI"

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
        pre_input_variables = self.qa_prompt.input_variables if self.qa_prompt is not None else []
        for input_variable in pre_input_variables:
            if input_variable in ["context", "question", "chat_history"]:
                continue

            if input_variable not in input_variables:
                input_variables[input_variable] = ''

        template = self.qa_prompt.content if self.qa_prompt is not None else DEFAULT_QA_TEMPLATE
        template = unstrict_formatter.format(template, **input_variables)

        return PromptTemplate(
          input_variables=["context", "question", "chat_history"],
          template=template,
          validate_template=False,
        )


    def get_embeddings(self):
        llm_config = None
        if 'llm' in self.agent.options:
            llm_config = self.agent.options['llm']

        openai_api_key = None
        if llm_config is not None:
            openai_api_key = llm_config.get('openai_api_key')
        return OpenAIEmbeddings(openai_api_key=openai_api_key)

    def load_combine_docs_chain(self, docs_llm: BaseLanguageModel, conversation: ConversationSchema, message: ChatMessage):
        qa_prompt = self.generate_qa_prompt(conversation, message)
        return load_qa_chain(docs_llm, chain_type="stuff", verbose=True, prompt=qa_prompt)


    async def _run(self, conversation: ConversationSchema, message: ChatMessage, **kwargs: Any)-> ChatMessage:
        self.memory.input_key = "question"
        self.memory.output_key = "answer"

        datastore = None
        if self.agent.datastores is not None and len(self.agent.datastores) > 0:
            if message.metadata is not None:
                datastore_id = message.metadata.get('datastore')
                if datastore_id is not None:
                    datastore = next((x for x in self.agent.datastores if x.id == datastore_id), None)
                    logging.debug(f'Choose given datastore: {datastore_id} of agent: {self.agent.id}')
            if datastore is None:
                datastore = self.agent.datastores[0].datastore
                if len(self.agent.datastores) == 0 or self.agent.datastores[0].datastore is None:
                    print('XXX agent datastore.datastore is none, self.agent: ', self.agent)
                logging.debug(f'Choose first datastore: {datastore} of agent: {self.agent.id}')

        if datastore is None:
            raise Exception("no datastore specified")

        score_threshold = pydash.get(message.metadata, 'score_threshold', 0.00)

        embedding = self.get_embeddings()

        # get datastore options
        options = None
        if datastore.options is not None:
            credentialsId = str(datastore.options.get('credentials_id'))
            credentials = await self.credentials_service.get_by_id(UUID(hex=credentialsId))
            if credentials is not None:
                options = credentials.data
                logging.info(f"choose custom datastore, provider: {datastore.provider}, options: {options}")


        if options is None:
            options = DEFAULT_QDRANT_OPTIONS
            logging.info(f"choose default datastore, provider: {datastore.provider}, options: {options}")

        _vectorstore = DatastoreManager.get(datastore.provider, options)
        vectorstore = _vectorstore.as_langchain(datastore.collection_name, embedding, content_payload_key="text")



        llm_options: Optional[Dict[str, Any]] = None
        if 'llm' in self.agent.options:
            llm_options = self.agent.options['llm']
    
        credentials = None
        if llm_options is not None:
            if "credentials_id" in llm_options:
                credentials_id = llm_options.pop("credentials_id")
                credentials = await self.credentials_service.get_by_id(credentials_id)

        # llm_streaming = await self.llm_manager.load(credentials, config=llm_config, stream_handler=stream_handler)

        llm = await self.llm_manager.load(credentials, llm_options)
        docs_llm = await self.llm_manager.load(credentials, llm_options, **kwargs)

        question_prompt = self.load_question_prompt(conversation, message)
        question_generator = LLMChain(llm=llm, prompt=question_prompt, verbose=True)
        docs_chain = self.load_combine_docs_chain(docs_llm, conversation, message)

        # RetrievalQA
        qa_chain = ConversationalRetrievalChain(
            memory=self.memory,
            question_generator=question_generator, 
            combine_docs_chain=docs_chain,
            retriever=vectorstore.as_retriever(search_type="similarity_score_threshold", search_kwargs={ "k":4, "score_threshold": score_threshold }),
            max_tokens_limit=3375,
            return_source_documents=True,
            verbose=True,
            response_if_no_docs_found=None,
        )

        response = await qa_chain.acall({"question": message.text, "chat_history": []})

        sent_at = int(datetime.now().timestamp() * 1000)

        return ChatMessage(
            id=str(uuid4()),
            conversation_id=message.conversation_id,
            text=response['answer'],
            sent_at=sent_at,
            from_user=ChatUser(
                id=str(self.agent.id),
                name=self.agent.name,
            ),
            to=ChatUser(
                id=message.from_user.id,
                name=message.from_user.name,
            ),
            metadata={
                "source_documents": response['source_documents'],
            },
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