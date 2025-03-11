from typing import List, Any, Dict
from bs4 import BeautifulSoup
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import urllib3
from vectorstore import Document
from asyncer import runnify
from core.datasource.loaders.context import LoaderContext
from repositories.sqlalchemy.datastore_repository import DatastoreRepository
from repositories.sqlalchemy.document_repository import DocumentRepository
from repositories.sqlalchemy.credentials_repository import CredentialsRepository
from db.celery_session import async_session
from core.file_storage.file_storage_manager import FileStorageManager
from models.datasource import DatasourceSchema

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WebsiteSpider(CrawlSpider):
    name = "website_spider"

    def __init__(self, datasource: DatasourceSchema = None, *args, **kwargs):
        super(WebsiteSpider, self).__init__(*args, **kwargs)
        self.datasource = datasource

    allowed_domains = [
    ]
    
    rules = (
        Rule(LinkExtractor(), callback="parse_item", follow=True),
    )

    def parse_item(self, response):
        datasource = self.datasource

        url = response.url
        # text = response.body.decode()
        soup = BeautifulSoup(response.body)
        text = soup.get_text()

        """Build metadata from BeautifulSoup output."""
        metadata: Dict[str, Any] = {
            "source_type": datasource.type,
            "source": url,
            "source_id": str(datasource.id),
            "url": url,
        }
        if title := soup.find("title"):
            metadata["title"] = title.get_text()
        if description := soup.find("meta", attrs={"name": "description"}):
            metadata["description"] = description.get("content", None)
        if html := soup.find("html"):
            metadata["language"] = html.get("lang", None)

        docs = [
            Document(
                text=text,
                metadata=metadata,
            )
        ]

        runnify(self._save)(docs)

        print('url: ', url)

    async def _save(self, docs: List[Document]):
        async with async_session() as db_session:
            datastore_repository = DatastoreRepository(db_session)
            document_repository = DocumentRepository(db_session)
            credentials_repository = CredentialsRepository(db_session)
            datastore = await datastore_repository.get_by_id(self.datasource.datastore_id)

        file_storage_manager = FileStorageManager()

        if not datastore:
            raise Exception("datastore not exists, need stop")

        context = LoaderContext(
            datastore=datastore,
            datasource=self.datasource,
            document_repository=document_repository,
            credentials_repository=credentials_repository,
            file_storage_manager=file_storage_manager,
        )
        
        await context.save(docs)


    def spider_closed(self, spider):
        print("spider_closed")

