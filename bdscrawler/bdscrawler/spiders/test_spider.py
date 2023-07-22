import urllib.parse

from bdscrawler.basecrawler.spiders.basespider import BaseSpider
from bdscrawler.basecrawler.logs.BaseLogging import BaseLogging
import scrapy


class QuotesSpider(BaseSpider):
    name = "quotes"
    domain = "https://quotes.toscrape.com/"
    start_urls = [
        "https://quotes.toscrape.com/page/1/"
    ]

    custom_settings = {
        'ITEM_PIPELINES': {
            'bdscrawler.basecrawler.pipelines.BasePipeline.SavingToDatabasePipeline': 400,
        }
    }
    def parse(self, response):
        self.current_page = response.url
        self.log(response.url)
        self.custom_logging.current(message=self.current_page)
        next_page = self.generate_next_page(self.current_page)
        print(response.body)
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse)

    def generate_next_page(self, current_page):
        index_page = 'https://quotes.toscrape.com/page/'
        number_page = current_page.split('/')[-2]
        number_page = int(number_page)
        next_page = number_page + 1
        if next_page == 4:
            return None
        next_url = index_page + str(next_page) + "/"
        return next_url
    def get_absolute_path(self, news_url):
        if self.domain in news_url:
            return news_url
        else:
            return urllib.parse.urljoin(self.domain, news_url)

    def recognize_url(self, news_url):
        if "page" in news_url:
            return 'index_page'
        else:
            return 'news_page'
