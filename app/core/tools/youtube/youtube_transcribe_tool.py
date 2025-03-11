from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from asyncer import asyncify
from typing import Type, List
from langchain.document_loaders import YoutubeLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains.qa_with_sources.loading import (
    load_qa_with_sources_chain,
)
from core.llm.manager import LLMManager
from asyncer import runnify



class YoutubeTranscribeInput(BaseModel):
    url: str = Field(description="the url of the given Youtube video")
    # language: str = Field(description="", default="en")
    question: str = Field(description="question about the given Youtube video.")



class YoutubeTranscribeTool(BaseTool):
    """Tool that transcribe a given YouTube Video."""

    llm_manager: LLMManager

    name = "youtube_transcribe"
    description = (
        "transcribe the content of a given youtube video."
        "You should enter a video url."
    )
    args_schema: Type[BaseModel] = YoutubeTranscribeInput

    def _run(self, url: str, question: str):
        # video_id = YoutubeTranscribeTool.extract_video_id(url)
        loader = YoutubeLoader.from_youtube_url(url, add_video_info=True)
        documents = loader.load()

        text_splitter=RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 100,
        )

        new_documents: List[Document] = []
        # split documents
        for document in documents:
            texts = text_splitter.split_text(document.page_content)
            for text in texts:
                new_documents.append(
                    Document(
                        page_content=text,
                        metadata={
                          "source": url,
                        }
                    )
                )
        print('new_documents: ', new_documents)

        if len(new_documents) > 0:
            llm = runnify(self.llm_manager.load)()
            
            chain = load_qa_with_sources_chain(llm, chain_type="map_reduce", verbose=True)
            # chain = load_summarize_chain(llm, chain_type="refine", verbose=True)
            output = chain(
                {"input_documents": new_documents, "question": question},
                return_only_outputs=True,
            )
            print("output: ", output)
            return output
        return ""

    # 这里不能用 position arg, 和 langchain 的实现有关
    async def _arun(self, url: str, question: str):
        return await asyncify(self._run)(url, question)