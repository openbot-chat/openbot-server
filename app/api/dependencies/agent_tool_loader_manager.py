from fastapi import Depends
from core.llm.manager import LLMManager
from .get_llm_manager import get_llm_manager

from core.agent_tool.agent_tool_loader_manager import AgentToolLoaderManager
from core.agent_tool.loaders.openapi_agent_tool_loader import OpenAPIAgentToolLoader
from core.agent_tool.loaders.zapier_nla_agent_tool_loader import ZapierNLAAgentToolLoader
from core.agent_tool.loaders.serpapi_agent_tool_loader import SerpAPIAgentToolLoader
from core.agent_tool.loaders.sql_database_agent_tool_loader import SQLDatabaseAgentToolLoader
from core.agent_tool.loaders.huggingface_agent_tool_loader import HuggingFaceAgentToolLoader
from core.agent_tool.loaders.youtube_search_agent_tool_loader import YoutubeSearchAgentToolLoader
from core.agent_tool.loaders.github_agent_tool_loader import GithubAgentToolLoader
from core.agent_tool.loaders.gmail_agent_tool_loader import GmailAgentToolLoader
from core.agent_tool.loaders.webpage_qa_agent_tool_loader import WebpageQAAgentToolLoader
from core.agent_tool.loaders.tiktok_agent_tool_loader import TiktokAgentToolLoader
from core.agent_tool.loaders.vectorstore_agent_tool_loader import VectorstoreAgentToolLoader
from core.agent_tool.loaders.datastore_agent_tool_loader import DatastoreAgentToolLoader
from core.agent_tool.loaders.dalle_agent_tool_loader import DalleAgentToolLoader
from core.agent_tool.loaders.llm_agent_tool_loader import LLMAgentToolLoader



def get_agent_tool_loader_manager(llm_manager: LLMManager = Depends(get_llm_manager, use_cache=True)) -> AgentToolLoaderManager:
    openapi_agent_tool_loader = OpenAPIAgentToolLoader(llm_manager)
    zapier_nla_agent_tool_loader = ZapierNLAAgentToolLoader(llm_manager)
    serpapi_agent_tool_loader = SerpAPIAgentToolLoader();
    sql_database_agent_tool_loader = SQLDatabaseAgentToolLoader(llm_manager)
    # huggingface_agent_tool_loader = HuggingFaceAgentToolLoader()
    youtube_search_agent_tool_loader = YoutubeSearchAgentToolLoader(llm_manager)
    github_agent_tool_loader = GithubAgentToolLoader()
    gmail_agent_tool_loader = GmailAgentToolLoader()
    webpage_qa_agent_tool_loader = WebpageQAAgentToolLoader(llm_manager)
    tiktok_agent_tool_loader = TiktokAgentToolLoader()
    vectorstore_agent_tool_loader = VectorstoreAgentToolLoader()
    datastore_agent_tool_loader = DatastoreAgentToolLoader()
    dalle_agent_tool_loader = DalleAgentToolLoader()
    llm_agent_tool_loader = LLMAgentToolLoader(llm_manager)

    agent_tool_loader_manager = AgentToolLoaderManager({
        "openapi": openapi_agent_tool_loader,
        "zapier": zapier_nla_agent_tool_loader,
        "serpapi":  serpapi_agent_tool_loader,
        "sql_database": sql_database_agent_tool_loader,
        # "huggingface": huggingface_agent_tool_loader,
        "youtube_search": youtube_search_agent_tool_loader,
        "github": github_agent_tool_loader,
        "gmail": gmail_agent_tool_loader,
        "webpage_qa": webpage_qa_agent_tool_loader,
        "tiktok": tiktok_agent_tool_loader,
        "vectorstore": vectorstore_agent_tool_loader,
        "datastore": datastore_agent_tool_loader,
        "dalle": dalle_agent_tool_loader,
        "llm": llm_agent_tool_loader,
    })

    return agent_tool_loader_manager