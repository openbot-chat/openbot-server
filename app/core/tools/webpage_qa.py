from typing import Type, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool, DuckDuckGoSearchRun
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains.qa_with_sources.loading import (
    BaseCombineDocumentsChain,
)
from asyncer import runnify



async def async_load_playwright(url: str) -> str:
    """Load the specified URLs using Playwright and parse using BeautifulSoup."""
    from bs4 import BeautifulSoup
    from playwright.async_api import async_playwright

    results = ""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.goto(url)

            page_source = await page.content()
            soup = BeautifulSoup(page_source, "html.parser")

            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            results = "\n".join(chunk for chunk in chunks if chunk)
        except Exception as e:
            results = f"Error: {e}"
        await browser.close()
    return results

def _get_text_splitter():
    return RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size=500,
        chunk_overlap=20,
        length_function=len,
    )



class WebpageQAInput(BaseModel):
    url: str = Field(description="webpage url")
    question: Optional[str] = Field(description="question about the webpage", default="summary the content")

class WebpageQATool(BaseTool):
    name = "query_webpage"
    description = (
        "Browse a webpage and retrieve the information relevant to the question."
    )
    args_schema: Type[BaseModel] = WebpageQAInput

    text_splitter: RecursiveCharacterTextSplitter = Field(
        default_factory=_get_text_splitter
    )
    qa_chain: BaseCombineDocumentsChain

    def _run(self, url: str, question: Optional[str] = "summary the content"):
        return runnify(self._arun)(url, question)

    async def _arun(self, url: str, question: Optional[str] = "summary the content"):
        """Useful for browsing websites and scraping the text information."""
        result = await async_load_playwright(url)
        docs = [Document(page_content=result, metadata={"source": url})]
        web_docs = self.text_splitter.split_documents(docs)

        # TODO 给定时间内缓存 web_docs 到 redis

        output = await self.qa_chain.acall(
            {"input_documents": web_docs, "question": question},
            return_only_outputs=True,
        )

        return output