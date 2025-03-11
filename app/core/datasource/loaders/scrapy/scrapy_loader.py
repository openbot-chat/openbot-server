from ..datasource_loader import DatasourceLoader
from ..context import LoaderContext
import logging
import click
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from .spider import WebsiteSpider
from asyncer import asyncify
from twisted.internet import reactor
from urllib.parse import urlparse


class ScrapyLoader(DatasourceLoader):
    async def load(self, context: LoaderContext):
        await asyncify(self._load)(context)

    def _load(self, context: LoaderContext):
        if not context.datasource.options:
            return

        url = context.datasource.options.get("url")
        if url is None:
            raise Exception("url not found")

        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        runner = CrawlerRunner(settings=get_project_settings())
        runner.crawl(WebsiteSpider, context.datasource, start_urls=[url], allowed_domains=[domain])        
        d = runner.join()
        # d.addBoth(lambda _: reactor.stop())
        reactor.run()

        logging.info(click.style(f'after crawl site: {url}', fg="green"))
