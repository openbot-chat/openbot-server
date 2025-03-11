from .datasource_loader import DatasourceLoader

from langchain.document_loaders import WebBaseLoader
from vectorstore.models import Document
from .context import LoaderContext

class WebPageLoader(DatasourceLoader):
    async def load(self, context: LoaderContext):
        url = context.datasource.options.get('url')
        if url is None:
            raise Exception("url not found")

        loader = WebBaseLoader(web_path=[url])
        documents = loader.load()

        docs = [Document(
            text=doc.page_content,
            metadata={
              **doc.metadata,
              "source_id": str(context.datasource.id),
              "source_type": context.datasource.type,
              "url": url,
            }
        ) for doc in documents]

        await context.save(docs)