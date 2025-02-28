from dotenv import load_dotenv
load_dotenv()

from langchain.tools.google_search import SerpAPIWrapper
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
import pytest


@pytest.mark.asyncio
async def test_openai_function_call():
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106")
    # Initialize the SerpAPIWrapper for search functionality
    #Replace <your_api_key> in openai_api_key="<your_api_key>" with your actual SerpAPI key.
    search = SerpAPIWrapper()

    # Define a list of tools offered by the agent
    tools = [
        Tool(
            name="Search",
            func=search.run,
            description="Useful when you need to answer questions about current events. You should ask targeted questions."
        ),
    ]
    mrkl = initialize_agent(tools, llm, agent=AgentType.OPENAI_MULTI_FUNCTIONS, verbose=True)
    output = mrkl.run("深圳和北京的天气如何? 今天硅谷有什么新闻")
    print("output: ", output)