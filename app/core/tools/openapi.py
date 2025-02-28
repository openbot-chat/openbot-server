from typing import Dict
from pydantic import BaseModel, Field
from langchain.utilities.openapi import OpenAPISpec
# from langchain.requests import Requests
from core.monkey_patching.tool import *
from langchain.tools.base import BaseTool
from langchain.chains.openai_functions.openapi import get_openapi_chain, openapi_spec_to_openai_fn, SimpleRequestChain
from models.credentials import CredentialsSchemaBase
from asyncer import runnify
from core.credentials.credentilas_helper import CredentialsHelper
import logging
from typing import Type, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain.schema import BasePromptTemplate
from langchain.schema.language_model import BaseLanguageModel
from langchain.chains.base import Chain

from asyncer import runnify



class OpenApiToolInput(BaseModel):
    input: str = Field(description="original user input")



class OpenApiTool(BaseTool):
    name = "openapi"
    description = (
        "useful for when you need to do API requests to a third-party service."
    )
    args_schema: Type[BaseModel] = OpenApiToolInput
    headers: Optional[Dict[str, str]]
    spec: str
    llm: Optional[BaseLanguageModel]
    prompt: BasePromptTemplate
    credentials: Optional[CredentialsSchemaBase]

    def get_chain(self) -> Chain:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        }

        if self.headers is not None:
            headers.update(self.headers)

        spec = OpenAPISpec.from_text(self.spec)

        openai_fns, call_api_fn = openapi_spec_to_openai_fn(spec)

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

        return get_openapi_chain(
            spec, 
            llm=self.llm,
            prompt=self.prompt, 
            verbose=True, 
            request_chain=SimpleRequestChain(
                request_method=lambda name, args: request_method(
                    name, args, credentials, headers=headers
                ),
                verbose=True,
            )
        )

    def _run(self, question: str):
        chain = self.get_chain()
        return chain.run(question)

    async def _arun(self, question: str):
        chain = self.get_chain()
        return await chain.arun(question, kwargs)
    



class OpenApiExecutor(BaseModel):
    spec: str

    async def run(args: Any):
        spec = OpenAPISpec.from_text(self.spec)
        print("base_url: ", spec.base_url)