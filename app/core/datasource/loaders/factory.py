from typing import Optional
from .datasource_loader import DatasourceLoader
from .text_loader import TextLoader
from .webpage_loader import WebPageLoader
from .file_loader import FileLoader
from .scrapy import ScrapyLoader
from .youtube_loader import YoutubeLoader
from .bilibili_loader import BilibiliLoader
from .airtable_loader import AirtableLoader
from .github_loader import GithubLoader



loaders = {
    "text": TextLoader,
    "file": FileLoader,
    "web_page": WebPageLoader,
    "website": ScrapyLoader,
    "youtube": YoutubeLoader,
    "bilibili": BilibiliLoader,
    "airtable": AirtableLoader,
    "github": GithubLoader,
}

class DatasourceLoaderFactory:    
    @staticmethod
    def create(type: str) -> Optional[DatasourceLoader]:
        if type in loaders:
            cls = loaders[type]
            return cls()
        return None