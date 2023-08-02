
from bdscrawler.basecrawler.spiders.basespider import BaseSpider
from scrapy.exceptions import CloseSpider
import scrapy
import pandas as pd
from bdscrawler.bdscrawler.items.AlonhadatItem import AlonhadatItem
from bdscrawler.bdscrawler.itemloaders.AlonhadatLoader import ALonhadatItemLoader
from bdscrawler.basecrawler.utils.helpers import *
class AlonhadatSpider(BaseSpider):
    name = 'alonhadat'
    start_urls = [
        "https://alonhadat.com.vn/nha-dat/can-ban/can-ho-chung-cu/1/ha-noi.html"
    ]
    domain = 'https://alonhadat.com.vn/'
    spider_code = '0001'
    number_old_request = 0
    max_old_request = 200
    number_error = 0

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 500,
            'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 510,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 420,
            'bdscrawler.basecrawler.middlewares.basemiddlewares.TorProxyMiddleware': 400,
            'bdscrawler.bdscrawler.middlewares.AlonhadatMiddlewares.CustomHeadersMiddleware': 410,
            'bdscrawler.bdscrawler.middlewares.AlonhadatMiddlewares.CustomRedirectMiddleware': 500,
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

        'FAKEUSERAGENT_PROVIDERS': [
            'scrapy_fake_useragent.providers.FakeUserAgentProvider',  # this is the first provider we'll try
            'scrapy_fake_useragent.providers.FakerProvider',
            # if FakeUserAgentProvider fails, we'll use faker to generate a user-agent string for us
            'scrapy_fake_useragent.providers.FixedUserAgentProvider',  # fall back to USER_AGENT value
        ],
        'CUSTOM_HEADER_ENABLED': True,
        'ITEM_PIPELINES': {
            'bdscrawler.bdscrawler.pipelines.AlonhadatPipelines.AlonhadatConvertPricePipline': 400,
            'bdscrawler.bdscrawler.pipelines.AlonhadatPipelines.AlonhadatExtractAddress': 300,
            'bdscrawler.basecrawler.pipelines.BasePipeline.SavingToDatabasePipeline': 500
        },
        'MAX_NUMBER_ERROR': 3,
        'TOR_IPROTATOR_ENABLED': True,
        'TOR_IPROTATOR_CHANGE_AFTER': 5,  # number of requests made on the same Tor's IP address
        'TOR_IPROTATOR_ALLOW_REUSE_IP_AFTER': 100,


    }
    def parse(self, response):
        if response.xpath('//*[@id="left"]/div[1]/div/@class').get() == 'notfound':
            self.current_page = 'end'
            self.custom_logging.current('end')
        elif 'xac-thuc-nguoi-dung' in response.url:
            self.number_error = self.number_error + 1
            if self.number_error <= self.settings.getint('MAX_NUMBER_ERROR', 3):
                self.custom_logging.debug(self.get_absolute_path(self.current_page), event='error by authen page')
            else:
                raise CloseSpider(reason="max time authen error")
        else:
            self.custom_logging.current(self.get_absolute_path(response.url))
            self.number_error = 0

            for item_selector in response.css('#left > div.content-items > div'):
                title = item_selector.xpath('./div[1]/div[1]/a/text()').get()
                published_at = item_selector.xpath('./div[1]/div[2]/text()').get()
                published_at = convert_time(published_at)

                news_url = item_selector.xpath('./div[1]/div[1]/a/@href').get()
                news_url = self.get_absolute_path(news_url)
                news_id = self.extract_id_from_url(news_url)

                res = self.update_old_item(news_id, published_at)
                if res == 0:
                    self.number_old_request = 0
                    self.list_request.append(news_url)
                    self.custom_logging.request(news_url)
                else:
                    self.number_old_request += 1

        self.current_page = self.get_absolute_path(self.generate_next_page(self.current_page))

        if self.number_old_request > self.max_old_request:
            self.custom_logging.current('end')
            self.current_page = 'end'

        next_page = self.generate_next_page(self.current_page)
        print(next_page)
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse, errback=self.errback_func)
        else:
            self.custom_logging.current('end')

            for url in self.list_request:
                news_id = self.extract_id_from_url(url)
                res = self.update_old_item(news_id, None)
                if res == 0:
                    yield scrapy.Request(url, callback=self.parse_news, errback=self.errback_func)
                else:
                    self.custom_logging.response(url)
    def parse_news(self, response):
        if 'xac-thuc-nguoi-dung' in response.url:
            self.number_error = self.number_error + 1
            if self.number_error <= self.settings.getint('MAX_NUMBER_ERROR', 3):
                self.custom_logging.debug(self.get_absolute_path(response.url), event='error by authen page')
            else:
                raise CloseSpider(reason="max time authen error")

            return None
        self.number_error = 0
        response_url = self.get_absolute_path(response.url)
        self.custom_logging.response(response_url)

        news = ALonhadatItemLoader(item=AlonhadatItem(), response=response)

        news.add_value('source', self.name)
        news.add_value('news_url', response_url)
        news.add_xpath('title', '//*[@id="left"]/div[1]/div[@class="title"]/h1/text()')

        moreinfor_loader = news.nested_xpath('//*[@id="left"]/div[1]/div[@class="moreinfor"]')
        moreinfor_loader.add_xpath('square', './/span[@class="square"]/span[2]/text()')
        moreinfor_loader.add_xpath('total_price', './/span[@class="price"]/span[2]/text()')

        news.add_xpath('address', '//*[@id="left"]/div[1]/div[@class="address"]/span[2]/text()')

        contact_infor = news.nested_xpath('//*[@id="right"]/div[1]/div/div[2]')
        contact_infor.add_xpath('author', './/div[@class="name"]/text()')
        contact_infor.add_xpath('contact', './/div[@class="fone"]/a/text()')
        news.add_xpath('published_at', '//*[@id="left"]/div[1]/div[@class="title"]/span/text()')

        news.add_xpath('description', '//*[@id="left"]/div[1]/div[2]/text()')
        table = response.xpath('//*[@id="left"]/div[1]/div[@class="moreinfor1"]/div[2]/table').get()
        df = pd.read_html(table)[0]

        table_1 = df[[0, 1]]
        table_2 = df[[2, 3]].rename(columns={2: 0, 3: 1}).iloc[0:5]
        table_3 = df[[4, 5]].rename(columns={4: 0, 5: 1}).iloc[0:5]

        df_infor = pd.concat([table_1, table_2, table_3], axis=0)
        df_infor[1] = df_infor[1].apply(str)

        df_infor.set_index(0, inplace=True)

        news.add_value('news_id', self.spider_code + df_infor.loc['Mã tin'][1])
        news.add_value('width', df_infor.loc['Chiều ngang'][1])
        news.add_value('length', df_infor.loc['Chiều dài'][1])
        news.add_value('direction', df_infor.loc['Hướng'][1])
        news.add_value('front_road', df_infor.loc['Đường trước nhà'][1])
        news.add_value('license', df_infor.loc['Pháp lý'][1])
        news.add_value('n_floors', df_infor.loc['Số lầu'][1])
        news.add_value('n_bedrooms', df_infor.loc['Số phòng ngủ'][1])
        news.add_value('n_dinning_rooms', df_infor.loc['Phòng ăn'][1])
        news.add_value('kitchen', df_infor.loc['Nhà bếp'][1])
        news.add_value('balcony', df_infor.loc['Sân thượng'][1])
        news.add_value('parking_lot', df_infor.loc['Chổ để xe hơi'][1])
        news.add_value('owner', df_infor.loc['Chính chủ'][1])

        try:
            project = df_infor.loc['Thuộc dự án'][1]
            news.add_value('project', project)
            news.add_xpath('project_url', '//*[@id="left"]/div[1]/div[5]/div[2]/table/tr[6]/td[2]/span/a/@href')
        except:
            news.add_value('project', '---')
            news.add_value('project_url', '---')

        return news.load_item()
    def extract_id_from_url(self, url):
        if self.recognize_url(url) != 'news_page':
            return None
        news_id = self.spider_code + url.split('-')[-1][:-5]
        return news_id

    def recognize_url(self, url):
        if 'xac-thuc-nguoi-dung' in url:
            return 'authen_page'
        elif 'nha-dat/can-ban/can-ho-chung-cu' in url:
            return 'index_page'
        else:
            return 'news_page'

    def generate_next_page(self, current_page):
        if current_page is None:
            return self.start_urls[0]
        if current_page == 'end':
            return None
        if self.recognize_url(current_page) == 'index_page':
            begin, end = current_page.rsplit('/', 1)
            if end == 'ha-noi.html':
                return 'https://alonhadat.com.vn/nha-dat/can-ban/can-ho-chung-cu/1/ha-noi/trang--2.html'
            else:
                page_number = int(extract_float_number(end))
                next_page_number = end.replace(str(page_number), str(page_number + 1))
                return begin + '/' + next_page_number
        return None

