from typing import List
from .datasource_loader import DatasourceLoader
from vectorstore.models import Document
from models.credentials import CredentialsSchemaBase 
import os
import logging
import click
from .context import LoaderContext


class TextLoader(DatasourceLoader):
    async def load(self, context: LoaderContext):
        if not context.datasource.options:
            return

        filename = context.datasource.options.get('filename')
        if filename is None:
            raise Exception("filename not found")

        key = f'datastores/{context.datasource.datastore_id}/{filename}'

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

        content = await file_storage.get_object(key)

        logging.info(click.style(f'download text file from s3: {key}', fg="green"))

        docs = [Document(
            text=content.decode(),
            metadata={
              "source_id": str(context.datasource.id),
              "source_type": context.datasource.type,
              "source": filename,
            }
        )]

        await context.save(docs)
