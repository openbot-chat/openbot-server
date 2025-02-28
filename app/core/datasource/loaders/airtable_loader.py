from .datasource_loader import DatasourceLoader
from vectorstore.models import Document
from .context import LoaderContext
from .errors import DatasourceLoadError

from pyairtable import Api
from asyncer import asyncify


class AirtableLoader(DatasourceLoader):
    async def load(self, context: LoaderContext):
        options = context.datasource.options or {}
        
        api_key = options.get("api_key")
        if api_key is None:
            raise DatasourceLoadError(context.datasource.id, "api_key not found")

        base_id = options.get("base_id")
        if base_id is None:
            raise DatasourceLoadError(context.datasource.id, "base_id not found")

        table_id = options.get("table_id")
        if table_id is None:
            raise DatasourceLoadError(context.datasource.id, "table_id not found")

        def sync_load():
            api = Api(api_key)
            table = api.table(base_id, table_id)
            return table.all()

        records = await asyncify(sync_load)()

        docs = [Document(
            text=str(record),
            metadata={
              "source_id": str(context.datasource.id),
              "source_type": context.datasource.type,
              "source": base_id + "_" + table_id,
              "base_id": base_id,
              "table_id": table_id,
            }
        ) for record in records]

        await context.save(docs)