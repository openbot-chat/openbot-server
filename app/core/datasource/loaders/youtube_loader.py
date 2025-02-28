from .datasource_loader import DatasourceLoader

from .langchain.youtube import YoutubeLoader as _YoutubeLoader
from langchain.document_loaders.blob_loaders.youtube_audio import YoutubeAudioLoader
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import OpenAIWhisperParser
from vectorstore.models import Document
from .context import LoaderContext
from asyncer import asyncify
import logging
from aiofiles.tempfile import TemporaryDirectory
import shutil



class YoutubeLoader(DatasourceLoader):
    async def load(self, context: LoaderContext):        
        options = context.datasource.options
        url = options.get('url')
        if url is None:
            raise Exception("url not found")
        args = {}
        if "translation" in options:
            args['translation'] = options['translation']


        async def download_and_transcribe():
            async with TemporaryDirectory(prefix=str(context.datasource.id)) as save_dir:
                try:
                    print('save_dir: ', save_dir)
                    failover_loader = GenericLoader(YoutubeAudioLoader([url], save_dir), OpenAIWhisperParser())
                    return await asyncify(failover_loader.load)()
                finally:
                    await asyncify(shutil.rmtree)(save_dir)
 

        loader = _YoutubeLoader.from_youtube_url(url, add_video_info=True, **args)
        try:
            documents = await asyncify(loader.load)()
        except Exception:
            # failover
            logging.error(f"Load Youtube video error, do failover")
            documents = await download_and_transcribe()

        if len(documents) == 0:
            logging.warn(f"Youtube {url} load 0 documents, do failover")
            documents = await download_and_transcribe()

        if len(documents) == 0:
            raise Exception(f"no documents loaded")

        docs = [Document(
            text=doc.page_content,
            metadata={
              **doc.metadata,
              "source_id": str(context.datasource.id),
              "source_type": context.datasource.type,
              "url": url,
            }
        ) for doc in documents]

        if len(docs) == 0:
            logging.warn(f"Youtube {url} load 0 documents")

        await context.save(docs)
  



