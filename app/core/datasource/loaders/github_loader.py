from .datasource_loader import DatasourceLoader

from langchain.document_loaders import GitLoader
from vectorstore.models import Document
from .context import LoaderContext
from asyncer import asyncify
from .errors import DatasourceLoadError
from aiofiles.tempfile import TemporaryDirectory
from urllib.parse import urlparse
import logging
import click



class GithubLoader(DatasourceLoader):
    async def load(self, context: LoaderContext):
        options = context.datasource.options or {}
        url = options.get('url')
        if url is None:
            raise DatasourceLoadError(context.datasource.id, "url not found")

        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split("/")  # type: ignore
        repo_name = path_parts[2]

        branch = options.get('branch', 'main')

        async with TemporaryDirectory() as temp_dir:
            repo_path = f"{temp_dir}/{repo_name}/"  # type: ignore
            logging.info(click.style(f"github loader, repo_path: {repo_path}", fg="green"))

            loader = GitLoader(
                clone_url=url,
                repo_path=repo_path,
                branch=branch,
            )
            
            l_docs = await asyncify(loader.load_and_split)()
            logging.info(click.style(f'load {len(l_docs)} documents from url: {url}', fg="green"))


        docs = [Document(
            text=doc.page_content,
            metadata={
              **doc.metadata,
              "source_id": str(context.datasource.id),
              "source_type": context.datasource.type,
              "url": url + '/' + doc.metadata.get('file_path'),
            }
        ) for doc in l_docs]

        await context.save(docs)