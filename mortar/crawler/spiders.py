from datetime import datetime

from bs4 import BeautifulSoup
from django.utils import timezone
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from mortar import documents


class WebCrawler(CrawlSpider):
    name = 'crawler'

    rules = (
        Rule(
            LinkExtractor(canonicalize=True, unique=True),
            follow=True,
            callback='parse_item',
        ),
    )

    custom_settings = {
        'USER_AGENT': '',
        'EXTENSIONS': {
            'mortar.crawler.extensions.TaskRevoked': 0,
        },
        'ROBOTSTXT_OBEY': True,
    }

    def __init__(self, *args, task, **kwargs):
        self.task = task
        self.index = self.task.crawler.index

        if 'start_urls' not in kwargs:
            kwargs['start_urls'] = self.task.crawler.urls.split('\n')

        super().__init__(*args, **kwargs)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')

        for element in soup(['script', 'style']):
            element.decompose()

        doc = documents.Document(
            url=response.url,
            referer=str(response.request.headers.get('Referer', None)),
            title=soup.title.string if soup.title else "",
            content=soup.get_text(),
            timestamp=datetime.strftime(timezone.now(), "%Y-%m-%dT%H:%M:%S.%f"),
        )

        doc.save(index=self.index)