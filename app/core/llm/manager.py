from typing import Dict, Any, Optional
from models.credentials import CredentialsSchemaBase
from langchain.chat_models import ChatOpenAI
from langchain.llms.loading import load_llm_from_config
from langchain.llms.base import BaseLLM
from langchain_deepseek import ChatDeepSeek
import logging
import click



class LLMManager:
    def __init__(self):
        ...

    async def load(self, credentials: Optional[CredentialsSchemaBase] = None, config: Optional[Dict[str, Any]] = None, **kwargs: Any) -> BaseLLM:
        _kwargs = kwargs.copy()

        
        stream_handler = None
        if "stream_handler" in _kwargs:
            stream_handler = _kwargs.pop('stream_handler')

        llm = None
        if not config:
            args = {
                "model_name": "gpt-3.5-turbo-1106", 
                "temperature": 0, 
                "verbose": True,
            }

            # llm = ChatOpenAI(**args, **_kwargs)
            llm = ChatDeepSeek(**args, **_kwargs)
        else:
            args = config.copy()
            if credentials is not None:
                args.update(credentials.data)
                logging.info(click.style(f"loading custom credentials: {credentials.data}", fg="yellow"))
            else:
                logging.info(click.style(f"loading default credentials", fg="yellow"))

            _type = args.get("_type", "")
            if _type == 'openai':
                model_name = args.get("model_name", "")
                if model_name.startswith("gpt-3.5-turbo") or model_name.startswith("gpt-4"):
                    logging.info(click.style(f"loading custom llm config: {args}", fg="yellow"))
                    args.pop("_type")
                    # llm = ChatOpenAI(**args, **_kwargs)
                    llm = ChatDeepSeek(**args, **_kwargs)
            if not llm:
                llm = load_llm_from_config(args)
                logging.info(click.style(f"loading custom llm config: {args}", fg="yellow"))

        if stream_handler is not None:
            llm.streaming = True
            llm.callbacks = [stream_handler]

        return llm
