from typing import List, Dict
from .datasource_loader import DatasourceLoader
from vectorstore.models import Document
from models.credentials import CredentialsSchemaBase 
import os
import logging
import click
from typing import Any
from urllib.parse import urlparse
from langchain.document_loaders import CSVLoader, PyPDFLoader, UnstructuredExcelLoader, TextLoader, ImageCaptionLoader
from langchain.document_loaders.word_document import UnstructuredWordDocumentLoader
from langchain.document_loaders.image import UnstructuredImageLoader
from langchain.document_loaders.base import BaseLoader
from langchain.document_loaders.generic import GenericLoader


from langchain.docstore.document import Document as LDocument
from aiofiles.tempfile import NamedTemporaryFile
import asyncio
from .context import LoaderContext
from langchain.document_loaders.parsers import OpenAIWhisperParser

from core.document.loaders.image_caption_loader import ImageCaptionLoader
from core.document.loaders.loader import DocumentLoader



class DummyFileLoader(BaseLoader):
    def __init__(self,  file_path: str):
        ...
    
    def load(self) -> List[LDocument]:
        return [
            LDocument(
                page_content=""
            )
        ]


def create_loader_func(cls: Any):
    def create_loader(file_path: str) -> BaseLoader:
      return cls(file_path)
    return create_loader

def create_voice_loader():
    def create_loader(file_path: str) -> BaseLoader:
        dir_path = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        return GenericLoader.from_filesystem(dir_path, glob=filename, parser=OpenAIWhisperParser())
    return create_loader


url_loader_funcs = {
    'jpg': ImageCaptionLoader, # ImageCaptionLoader
    'jpeg': ImageCaptionLoader, # ImageCaptionLoader
    'png': ImageCaptionLoader, # ImageCaptionLoader
    'webp': ImageCaptionLoader,# ImageCaptionLoader
    'gif': ImageCaptionLoader, # ImageCaptionLoader
    'heic': ImageCaptionLoader,
}



l_loader_funcs = {
    'txt': create_loader_func(TextLoader),
    'csv': create_loader_func(CSVLoader),
    'pdf': create_loader_func(PyPDFLoader),
    'xlsx': create_loader_func(UnstructuredExcelLoader),
    'doc': create_loader_func(UnstructuredWordDocumentLoader),
    'docx': create_loader_func(UnstructuredWordDocumentLoader),
    'mp3': create_voice_loader(),
    'mp4': create_voice_loader(),
}


class FileLoader(DatasourceLoader):
    async def load(self, context: LoaderContext):
        if not context.datasource.options:
            return

        filename = context.datasource.options.get('filename')
        url = context.datasource.options.get('url')
        if url is None:
            raise Exception("url not found")

        parsed_url = urlparse(url)
        key = parsed_url.path[1:]
        file_name, file_extension = os.path.splitext(key)
        file_type = file_extension[1:].lower()
        print(f'file_type: {file_type}')

        # 先从 url 加载
        loader_cls = url_loader_funcs.get(file_type)
        if loader_cls is not None:
            loader = loader_cls(url)
            docs = await loader.load()
            for doc in docs:
                if not doc.text or len(doc.text) < 4:
                     doc.text = context.datasource.name

                if not doc.metadata:
                    continue

                doc.metadata['source_id'] = str(context.datasource.id)
                doc.metadata['source'] = url
                doc.metadata['url'] = url
        else:
            file_storage = context.file_storage_manager.load("s3", CredentialsSchemaBase(
                type="aws",
                name="aws s3",
                data={
                    "region": os.getenv("S3_REGION"),
                    "use_ssl": os.getenv("S3_SSL"),
                    "endpoint": os.getenv("S3_ENDPOINT"),
                    "bucket": os.getenv("S3_BUCKET"),
                    "secret_key": os.getenv("S3_SECRET_KEY"),
                    "access_key": os.getenv("S3_ACCESS_KEY"),
                },
            ))

            def do_load(file_type: str, file_path: str) -> List[LDocument]:
                create_loader_func = l_loader_funcs.get(file_type)
                if not create_loader_func:
                    raise Exception(f'file loader for type {file_type} not found')
                loader = create_loader_func(file_path)

                return loader.load()
                
            async with NamedTemporaryFile(mode="wb", delete=True) as async_buffer:
                file_path = async_buffer.name
                await file_storage.download_fileobj(key, async_buffer)
                logging.info(click.style(f'download file from s3: {key}, file_path: {file_path}', fg="green"))

                await async_buffer.seek(0)

                l_docs = await asyncio.to_thread(
                    do_load,
                    file_type,
                    file_path,
                )
                logging.info(click.style(f'load {len(l_docs)} documents from file_path: {file_path}', fg="green"))

            print("fuckdocs: ", l_docs)

            docs = [Document(
                text=doc.page_content if len(doc.page_content) >= 6 else context.datasource.name,
                metadata={
                  **doc.metadata,
                  "source_id": str(context.datasource.id),
                  "source_type": context.datasource.type,
                  "source": url,
                  "url": url,
                  "file_type": file_type,
                }
            ) for doc in l_docs]


        await context.save(docs)