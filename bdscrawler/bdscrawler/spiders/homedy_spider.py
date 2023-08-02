from bdscrawler.basecrawler.spiders.basespider import BaseSpider
from bdscrawler.basecrawler.utils.helpers import *
from scrapy.exceptions import CloseSpider
from bdscrawler.bdscrawler.items.HomedyItem import HomedyItem
from bdscrawler.bdscrawler.itemloaders.HomedyLoader import HomedyItemLoader
import scrapy
import pandas as pd

class HomedySpider(BaseSpider):
    name = 'homedy'
    start_urls = [
        "https://homedy.com/ban-can-ho-ha-noi/p1"
    ]

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 500,
            'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 510,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 420,
            'bdscrawler.basecrawler.middlewares.basemiddlewares.TorProxyMiddleware': 400,
            'bdscrawler.bdscrawler.middlewares.HomedyMiddlewares.CustomHeadersMiddleware': 410,
            'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': None,
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
        'ITEM_PIPELINES': {
            'bdscrawler.bdscrawler.pipelines.HomedyPipelines.HomedyConvertPricePipline': 400,
            'bdscrawler.bdscrawler.pipelines.HomedyPipelines.HomedyExtractAddress': 300,
            'bdscrawler.basecrawler.pipelines.BasePipeline.SavingToDatabasePipeline': 500
        },
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429, 403],
        'RETRY_PRIORITY_ADJUST': -1,
        'CUSTOM_HEADER_ENABLED': True,

    }
    domain = 'https://homedy.com/'
    list_request = list()
    spider_code = '0002'
    number_old_request = 0
    max_old_request = 100
    number_error = 0

    def parse(self, response):

        self.current_page = self.get_absolute_path(response.url)
        self.custom_logging.current(self.current_page)

        for item_selector in response.xpath('//*[@id="MainPage"]/div[3]/div[2]/div'):
            item_class = item_selector.xpath('./@class').get()
            if 'product-item' not in item_class:
                continue

            infor_pane = item_selector.xpath('./div/h3/a')
            news_url = infor_pane.xpath('./@href').get()
            title = infor_pane.xpath('./@title').get()
            description = item_selector.xpath('./div/div[1]/text()').get()
            product_unit = item_selector.xpath('./div/ul')

            total_price = product_unit.xpath('./li[1]/span/text()').get()
            square = product_unit.xpath('./li[2]/span/text()').get()
            price_per_m2 = product_unit.xpath('./li[3]/text()').get()
            address = product_unit.xpath('./li[4]/@title').get()

            news_id = self.extract_id_from_url(news_url)
            res = self.update_old_item(news_id, None)

            if res == 0:
                self.number_old_request= 0
                self.custom_logging.request(self.get_absolute_path(news_url))
                self.list_request.append(self.get_absolute_path(news_url))
            else:
                self.number_old_request += 1
                print(self.number_old_request)

        next_page = self.generate_next_page(self.current_page)
        if next_page is not None and self.number_old_request < self.max_old_request:
            yield scrapy.Request(next_page, callback=self.parse, errback=self.errback_func)
        else:
            self.custom_logging.current('end')
            for url in self.list_request:
                yield scrapy.Request(url, callback=self.parse_news, errback=self.errback_func)

    def parse_news(self, response):
        news = HomedyItemLoader(item=HomedyItem(), response=response)
        self.custom_logging.response(self.get_absolute_path(response.url))
        news.add_value('news_url', response.url)
        news.add_xpath('title',
                       '/html/body/div[1]/div[5]/div[@class="float-in"]/div[2]/div/div[1]/div/div[1]/div/h1/text()')
        news.add_xpath('address',
                       '/html/body/div[1]/div[5]/div[@class="float-in"]/div[2]/div/div[1]/div/div[1]/div/div[2]//span/text()')
        news.add_xpath('total_price',
                       '/html/body/div[1]/div[5]/div[@class="float-in"]/div[2]/div/div[1]/div/div[1]/div/div[3]/div[1]/div[1]/strong/span/text()')
        news.add_xpath('total_price',
                       '/html/body/div[1]/div[5]/div[@class="float-in"]/div[2]/div/div[1]/div/div[1]/div/div[3]/div[1]/div[1]/strong/text()')
        news.add_xpath('price_per_m2',
                       '/html/body/div[1]/div[5]/div[@class="float-in"]/div[2]/div/div[1]/div/div[1]/div/div[3]/div[1]/div[1]/em/span[1]/text()')
        news.add_xpath('price_per_m2',
                       '/html/body/div[1]/div[5]/div[@class="float-in"]/div[2]/div/div[1]/div/div[1]/div/div[3]/div[1]/div[1]/em/span[2]/text()')
        news.add_xpath('square',
                       '/html/body/div[1]/div[5]/div[@class="float-in"]/div[2]/div/div[1]/div/div[1]/div/div[3]/div[1]/div[2]/strong/span/text()')
        news.add_xpath('author',
                       '/html/body/div[1]/div[5]/div[@class="float-in"]/div[2]/div/div[1]/div/div[@class="agent-inpage"]/div[1]/div[@class="agent-inpage-content"]/div[@class="info"]/div[@class="flex-name"]/a[1]/h3/text()')
        news.add_xpath('contact',
                       '/html/body/div[1]/div[5]/div[@class="float-in"]/div[2]/div/div[1]/div/div[@class="agent-inpage"]/div[1]/div[@class="agent-inpage-content"]/div[@class="operation"]/a[2]/div[@class="mb"]/span[@class="mobile-number"]/span[@class="mobile-visible-part"]/text()')
        news.add_xpath('project',
                       '/html/body/div[1]/div[5]/div[@class="float-in"]/div[2]/div/div[1]/div/div[6]/div/div/div/div/div[2]/a/text()')
        news.add_xpath('project_url',
                       '/html/body/div[1]/div[5]/div[@class="float-in"]/div[2]/div/div[1]/div/div[6]/div/div/div/div/div[2]/a/@href')
        news.add_xpath('published_at',
                       '/html/body/div[1]/div[5]/div[@class="float-in"]/div[2]/div/div[1]/div/div[@class="product-info"]/div[1]/p[2]/text()')
        news.add_xpath("news_id",
                       '/html/body/div[1]/div[5]/div[@class="float-in"]/div[2]/div/div[1]/div/div[@class="product-info"]/div[4]/p[2]/text()')
        news.add_value('source', self.name)
        return news.load_item()

    def generate_next_page(self, current_page):
        if current_page == 'end':
            return None
        if current_page == 'https://homedy.com/ban-can-ho-ha-noi/p200':
            return None
        if current_page is None:
            return self.start_urls[0]

        begin, end = current_page.rsplit('/', 1)
        try:
            page_number = int(extract_float_number(end))
        except Exception as e:
            return None
        next_page_number = end.replace(str(page_number), str(page_number + 1))
        return begin + '/' + next_page_number

    def extract_id_from_url(self, news_url):
        news_id = news_url.strip().split('-')[-1][2:]
        return self.spider_code + news_id

    def recognize_url(self, news_url):
        if 'ban-can-ho-ha-noi' in news_url:
            return 'index_page'
        else:
            return 'news_page'
