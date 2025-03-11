from .datasource_loader import DatasourceLoader

from langchain.document_loaders import BiliBiliLoader as _BiliBiliLoader
from vectorstore.models import Document
from .context import LoaderContext
from asyncer import asyncify

class BilibiliLoader(DatasourceLoader):
    async def load(self, context: LoaderContext):
        options = context.datasource.options
        urls = options.get('urls')
        if urls is None:
            raise Exception("urls not found")

        print("bilibili: ", urls)

        loader = _BiliBiliLoader(urls)
        documents = await asyncify(loader.load)()

        docs = [Document(
            text=doc.page_content,
            metadata={
              "source_type": context.datasource.type,  
              "source_id": str(context.datasource.id),
              "source": doc.metadata.get('source'),
              "url": doc.metadata.get('url'),
            }
        ) for doc in documents]

        await context.save(docs)