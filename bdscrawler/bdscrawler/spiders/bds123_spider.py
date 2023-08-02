import urllib.parse

from bdscrawler.basecrawler.spiders.basespider import BaseSpider
from bdscrawler.basecrawler.logs.BaseLogging import BaseLogging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from bdscrawler.bdscrawler.items.BDS123Item import BDS123Item
from bdscrawler.bdscrawler.itemloaders.BDS123Loader import BDS123ItemLoader
from scrapy.exceptions import CloseSpider
from bdscrawler.bdscrawler.utils.BDS123Helpers import *
from bdscrawler.basecrawler.utils.helpers import convert_time
import scrapy

class BDS123Spider(BaseSpider):
    name = 'bds123'
    start_urls = ['https://bds123.vn/ban-can-ho-chung-cu-ha-noi.html?orderby=moi-nhat&page=1']
    domain = 'https://bds123.vn/'
    spider_code = '0003'
    number_error = 0
    number_old_request = 0
    max_old_request = 100
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 500,
            'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 510,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 410,
            'bdscrawler.basecrawler.middlewares.basemiddlewares.TorProxyMiddleware': 400,
            'bdscrawler.bdscrawler.middlewares.BDS123Middlewares.BDS123CustomHeadersMiddeware': 420,
            'bdscrawler.bdscrawler.middlewares.BDS123Middlewares.CustomRedirectMiddleware': 500,
            'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
            'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': None,
            # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': 300
        },
        'CUSTOM_REDIRECT_ENABLED': True,
        'REDIRECT_MAX_TIMES': 3,
        'REDIRECT_PRIORITY_ADJUST': 1,
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 2,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429],
        'ITEM_PIPELINES': {
            'bdscrawler.bdscrawler.pipelines.BDS123Pipelines.BDS123ProcessAddressPipeline': 300,
            'bdscrawler.bdscrawler.pipelines.BDS123Pipelines.BDS123ProcessPricePipeline': 400,
            'bdscrawler.basecrawler.pipelines.BasePipeline.SavingToDatabasePipeline': 500
        },
        'FAKEUSERAGENT_PROVIDERS': [
            'scrapy_fake_useragent.providers.FakeUserAgentProvider',  # this is the first provider we'll try
            'scrapy_fake_useragent.providers.FakerProvider',
            # if FakeUserAgentProvider fails, we'll use faker to generate a user-agent string for us
            'scrapy_fake_useragent.providers.FixedUserAgentProvider',  # fall back to USER_AGENT value
        ],
        'TOR_IPROTATOR_ENABLED': True,
        'TOR_IPROTATOR_CHANGE_AFTER': 5,  # number of requests made on the same Tor's IP address
        'TOR_IPROTATOR_ALLOW_REUSE_IP_AFTER': 100,
        'CUSTOM_HEADER_ENABLED': True,
    }
    def parse_news(self, response):
        pass

    def parse(self, response):
        if response.status != 200:
            self.current_page = self.generate_next_page(self.current_page)
            next_page = self.generate_next_page(self.current_page)
            yield scrapy.Request(next_page, callback=self.parse)
        if response.xpath('//*[@id="main"]/div[contains(@class, "leftCol")]/section[contains(@class, "section-post-listing")]/div[contains(@class, "listing-empty")]').get():
            self.current_page = 'end'
            self.custom_logging.current('end')
            for url in self.list_request:
                yield scrapy.Request(url, callback=self.parse_news)
        else:
            for item_selector in response.xpath('//*[@id="main"]/div[contains(@class, "leftCol")]/section[contains(@class, "section-post-listing")]/div[contains(@class, "post-listing")]/li[contains(@class, "item")]'):
                news = BDS123ItemLoader(item=BDS123Item())
                news_url = item_selector.xpath('./a/@href').get()
                news_url = self.get_absolute_path(news_url)

                news_id = self.extract_id_from_url(news_url)
                news_id = self.spider_code + news_id

                infor_pane = item_selector.xpath('./a/aside[contains(@class, "post-aside")]')

                title = infor_pane.xpath('./h3[contains(@class, "title")]/text()').get()

                meta_pane = infor_pane.xpath('./div[contains(@class, "meta")]')
                total_price = meta_pane[0].xpath('./span[contains(@class, "price")]/text()').get()

                price_unit = meta_pane[0].xpath('./span[contains(@class, "price")]/i/text()').get()

                infor_feature_pane = meta_pane[0].xpath('./div[contains(@class, "info-features")]')

                square = infor_feature_pane.xpath('./span[contains(i/@class, "expand")]/text()').get()

                n_bedrooms = infor_feature_pane.xpath('./span[contains(i/@class, "bed")]/text()').get()

                n_baths = infor_feature_pane.xpath('./span[contains(i/@class, "bath")]/text()').get()

                published_at = meta_pane[0].xpath('./span[contains(@class, "time")]/@title').get()

                last_time_in_page = meta_pane[0].xpath('./span[contains(@class, "time")]/text()').get()

                address = meta_pane[1].xpath('./p[contains(@class, "post-address")]/span/text()').get()

                description = infor_pane.xpath('./p[contains(@class, "summary")]/text()').get()

                author = meta_pane[2].xpath('./div[contains(@class, "post-author")]/span/text()').get()

                res = self.update_old_item(news_id, convert_time(last_time_in_page))
                if res != 0:
                    if res == 2:
                        self.number_old_request += 1
                    continue
                self.number_old_request = 0

                news.add_value('source', self.name)
                news.add_value('news_url', news_url)

                news.add_value('news_id', news_id)

                news.add_value('title', title)

                news.add_value('total_price', total_price)

                news.add_value('price_unit', price_unit)

                news.add_value('square', square)

                news.add_value('n_bedrooms', n_bedrooms)

                news.add_value('n_baths', n_baths)

                news.add_value('published_at', published_at)

                news.add_value('last_time_in_page', last_time_in_page)

                news.add_value('address', address)

                news.add_value('description', description)

                news.add_value('author', author)

                yield news.load_item()
            self.current_page = response.url
            self.custom_logging.current(self.get_absolute_path(response.url))
            if self.number_old_request < self.max_old_request:
                next_page = self.generate_next_page(self.current_page)
                yield scrapy.Request(next_page, callback=self.parse)
            else:
                self.custom_logging.current('end')
                raise CloseSpider(reason='finished by reach old news')

    def extract_id_from_url(self, news_url):
        if news_url:
            return news_url.split('-')[-1][2:-5]
        return None

    def generate_next_page(self, current_page):
        if self.recognize_url(current_page) == 'index_page':
            parsed_url = urlparse(current_page)

            query_params = parse_qs(parsed_url.query)

            number_page = int(query_params.get('page', [1])[0])

            next_page = number_page + 1

            query_params['page'] = [str(next_page)]

            update_url = urlunparse(parsed_url._replace(query=urlencode(query_params, doseq=True)))

            return update_url
        return None

    def recognize_url(self, news_url):
        if 'ban-can-ho-chung-cu-ha-noi.html' in news_url:
            return 'index_page'
        return 'unknown'

