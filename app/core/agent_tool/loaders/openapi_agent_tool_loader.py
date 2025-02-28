from .agent_tool_loader import AgentToolLoader
from typing import List, Dict
from pydantic import BaseModel, Field
from langchain.tools.openapi.utils.openapi_utils import OpenAPISpec
# from langchain.requests import Requests
from core.llm import LLMManager
from core.monkey_patching.tool import *
from langchain.tools.base import BaseTool
from langchain.chains.openai_functions.openapi import get_openapi_chain, openapi_spec_to_openai_fn, SimpleRequestChain
from langchain.prompts import ChatPromptTemplate
from slugify import slugify
from models.agent_tool import AgentToolSchema
from models.credentials import CredentialsSchemaBase
from models.conversation import ConversationSchema
from asyncer import runnify
from core.credentials.credentilas_helper import CredentialsHelper
import logging
from langchain.chains import OpenAPIEndpointChain
from langchain.requests import Requests
from requests.auth import AuthBase



class CredentialsAuth(AuthBase):
    def __init__(self, credentials: Optional[CredentialsSchemaBase]):
        self.credentials = credentials

    def __call__(self, r):
        if self.credentials is not None:
            runnify(CredentialsHelper.pre_authenticate)(self.credentials)

        options: Dict[str, Any] = {
          "headers":  r.headers,
        }

        if self.credentials is not None:
            options = runnify(CredentialsHelper.authenticate)(self.credentials, options)
        
        r.headers = options.get("headers", {})

        return r





# 参考: https://github.com/homanp/superagent/blob/52b506ae7f7443796e8ad5985b8f2b7ba9b2ce7c/app/lib/tools.py#L20

"""
class ToolDescription(Enum):
    SEARCH = "useful for when you need to search for answers on the internet. You should ask targeted questions."
    WOLFRAM_ALPHA = "useful for when you need to do computation or calculation."
    REPLICATE = "useful for when you need to create an image."
    ZAPIER_NLA = "useful for when you need to do tasks."
    AGENT = "useful for when you need help completing something."
    OPENAPI = "useful for when you need to do API requests to a third-party service."
"""

class OpenApiToolInput(BaseModel):
    input: str = Field(description="original user input")


class OpenAPIAgentToolLoader(AgentToolLoader):
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager

    async def load(
        self, 
        agent_tool: AgentToolSchema, 
        credentials: Optional[CredentialsSchemaBase] = None, 
        conversation: Optional[ConversationSchema] = None,
    ) -> List[BaseTool]:
        tool_options = agent_tool.tool.options
        if not tool_options:
            raise Exception("config not found")

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        }

        agent_tool_headers = agent_tool.options.get("headers")
        if agent_tool_headers is not None:
            headers.update(agent_tool_headers)

        spec_text = str(tool_options.get("spec"))
        # 根据 credentials load
        _type = "openai"
        llm = await self.llm_manager.load()

        # spec_dict = json.loads(spec_text)
        # spec = OpenAPISpec.from_spec_dict(spec_dict)
        spec = OpenAPISpec.from_text(spec_text)

        openai_fns, call_api_fn = openapi_spec_to_openai_fn(spec)

        chat_context = None
        if conversation is not None:
            items: List[str] = []
            items.append(f"You and the human talk in {conversation.provider or 'Openbot platform'}")
            items.append(f"Current conversation id: {conversation.id}")
            if conversation.user_id is not None:
                items.append(f"Human's User ID: {conversation.user_id}")
            chat_context = "\n".join(items)

        def request_method(
            name: str, 
            args: dict,
            credentials: Optional[CredentialsSchemaBase] = None,
            headers: Optional[dict] = None,
            params: Optional[dict] = None,
        ) -> Any:
            if credentials is not None:
                runnify(CredentialsHelper.pre_authenticate)(credentials)

            options: Dict[str, Any] = {
              "headers":  headers,
              "params": params,
            }
            if credentials is not None:
                options = runnify(CredentialsHelper.authenticate)(credentials, options)

            try:
                logging.info(f"openapi tool call: {name}, {args}, headers: {headers}")

                return call_api_fn(name, args, headers=options.get("headers"), params=options.get("params"), timeout=5*60)
            except Exception as e:
                if credentials is not None:
                    # access_token 过期等
                    runnify(CredentialsHelper.pre_authenticate)(credentials)
                    return call_api_fn(name, args, headers=options.get("headers"), params=options.get("params"), timeout=5*60)
                else:
                    raise e


        prompt = ChatPromptTemplate.from_template(
            f"""{chat_context}
Use the provided API's to respond to this user query:\n\n{"{query}"}"""
        )

        chain = get_openapi_chain(
            spec, 
            llm=llm,
            prompt=prompt, 
            verbose=True, 
            request_chain=SimpleRequestChain(
                request_method=lambda name, args: request_method(
                    name, args, credentials, headers=headers
                ),
                verbose=True,
            )
        )

        return [
            Tool(
              name=str(agent_tool.tool.id),
              description=agent_tool.description or agent_tool.tool.description or "useful for when you need to do API requests to a third-party service.",
              func=chain.run,
              coroutine=chain.arun,
              args_schema=OpenApiToolInput if _type == "openai" else None,
              return_direct=agent_tool.return_direct or agent_tool.tool.return_direct
          )
        ]

        """
        api_title = spec.info.title

        if not spec.paths:
            return []


        auth = CredentialsAuth(credentials)
        requests = Requests(auth=auth, headers=headers)

        http_operation_tools: List[Tool] = []
        for path in spec.paths:
            for method in spec.get_methods_for_path(path):
                api_operation = APIOperation.from_openapi_spec(spec, path, method)
                
                #chain = OpenAIInvokeChain.from_api_operation(
                #    api_operation,
                #    requests=requests,
                #    verbose=True,
                #)
                chain = OpenAPIEndpointChain.from_api_operation(
                    api_operation,
                    llm,
                    requests=requests,
                    verbose=True,
                    # return_intermediate_steps=True,  # Return request and response text
                )


                expanded_name = (
                    f'{api_title.replace(" ", "_")}_{chain.api_operation.operation_id}'
                )
                description = (
                    f"I'm an AI from {api_title}. Instruct what you want,"
                    " and I'll assist via an API with description:"
                    f" {chain.api_operation.description}"
                )
                tool = Tool(
                    name=expanded_name, 
                    func=chain.run, 
                    description=description,
                )

                http_operation_tools.append(tool)

        return http_operation_tools
        """
