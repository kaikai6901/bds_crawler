import datetime

import scrapy
from bdscrawler.bdscrawler.settings import ITEM_DATABASE, ITEM_COLLECTION
from bdscrawler.basecrawler.logs.BaseLogging import BaseLogging
from bdscrawler.basecrawler.databaseservice.logging_service import LoggingDatabaseService
from bdscrawler.basecrawler.dao.MongoDB import MongoDB
from bdscrawler.basecrawler.utils.tor_controller import TorController
from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection
from scrapy import signals
from scrapy.exceptions import CloseSpider
import urllib.parse
class BaseSpider(scrapy.Spider):
    spider_code: str
    custom_logging: BaseLogging
    client: MongoClient
    collection: Collection
    current_page: str
    list_request: list
    max_old_request: int
    number_old_request: int
    domain: str
    ignore_runtime_before: bool
    ignore_old_request: bool
    start_urls: list
    logging_service: LoggingDatabaseService
    number_error: int
    tor_controller: TorController

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signals.spider_opened)
        crawler.signals.connect(spider.spider_error, signals.spider_error)
        crawler.signals.connect(spider.request_left_downloader, signals.request_left_downloader)
        crawler.signals.connect(spider.headers_received, signals.headers_received)
        crawler.signals.connect(spider.response_downloaded, signals.response_downloaded)
        crawler.signals.connect(spider.item_error, signals.item_error)
        crawler.signals.connect(spider.item_dropped, signals.item_dropped)
        crawler.signals.connect(spider.item_scraped, signals.item_scraped)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def start_requests(self):
        if not self.current_page:
            for url in self.start_urls:
                yield scrapy.Request(url, callback=self.parse, errback=self.errback_func, priority=1)
        else:
            next_page = self.generate_next_page(self.current_page)
            if next_page is not None:
                yield scrapy.Request(next_page, callback=self.parse, errback=self.errback_func, priority=1)
            else:
                for news_url in self.list_request:
                    yield scrapy.Request(news_url, callback=self.parse_news, errback=self.errback_func)


    def parse(self, response):
        print(response.text)

    def parse_news(self, response):
        pass

    def spider_opened(self, spider):
        mongo_dao = MongoDB()
        self.client = mongo_dao.get_client()
        try:
            mongo_dao.test_connection()
        except:
            raise CloseSpider(reason="Can't connect to database")

        self.collection = self.client[ITEM_DATABASE][ITEM_COLLECTION]
        self.custom_logging = BaseLogging(self)
        self.custom_logging.init_log()
        self.logging_service = LoggingDatabaseService(self.custom_logging)
        if self.ignore_old_request:
            self.max_old_request = 1e5
        if self.ignore_runtime_before:
            self.current_page = None
            self.list_request = list()
        else:
            current_page, list_request = self.logging_service.read_log()
            self.current_page = current_page
            self.list_request = list_request

        self.tor_controller = TorController(allow_reuse_ip_after=self.settings.getint('TOR_IPROTATOR_ALLOW_REUSE_IP_AFTER', 100))

    def spider_error(self, failure, response, spider):
        error_message = failure.getErrorMessage()
        message = {
            'failure': error_message,
            'response_url': response.url,
            'status_code': response.status,
            'response_headers': response.headers.to_unicode_dict(),
            'response_type': self.recognize_url(response.url)
        }
        self.custom_logging.log(event='spider_error', message=message)
        self.custom_logging.debug(message, event='spider_error')

    def request_left_downloader(self, request, spider):
        message = {
            'request_url': request.url,
            'request_headers': request.headers.to_unicode_dict(),
            'request_type': self.recognize_url(request.url)
        }
        self.custom_logging.log(event='request_left_downloader', message=message)

    def headers_received(self, headers, body_length, request, spider):
        message = {
            'request_url': request.url,
            'request_headers': request.headers.to_unicode_dict(),
            'response_headers': headers.to_unicode_dict(),
            'request_type': self.recognize_url(request.url)
        }
        self.custom_logging.log(event='headers_received', message=message)
        self.custom_logging.debug(message, event='headers_received')

    def response_downloaded(self, response, request, spider):
        message = {
            'request_url': request.url,
            'request_headers': request.headers.to_unicode_dict(),
            'response_url': response.url,
            'response_headers': response.headers.to_unicode_dict(),
            'request_type': self.recognize_url(request.url),
            'status_code': response.status
        }
        self.custom_logging.log(event='response_downloaded', message=message)

    def item_error(self, item, response, spider, failure):
        message = {
            'response_url': response.url,
            'response_headers': response.headers.to_unicode_dict(),
            'status_code': response.status,
            'failure': failure.getErrorMessage()

        }
        self.custom_logging.log(event='item_error', message=message)
        self.custom_logging.debug(message, event='item_error')

    def item_dropped(self, item, response, exception, spider):
        message = {
            'response_url': response.url,
            'response_headers': response.headers.to_unicode_dict(),
            'status_code': response.status,
            'exception': str(exception)
        }
        self.custom_logging.log(event='item_dropped', message=message)
        self.custom_logging.debug(message, event='item_dropped')

    def item_scraped(self, item, response, spider):
        message = {
            'response_url': response.url,
        }
        self.custom_logging.log(event='item_scraped', message=message)

    def spider_closed(self, spider, reason):
        self.custom_logging.debug(message=reason)
        self.log(reason)
        if self.check_spider_finished():
            reason = 'finished'
        else:
            reason = 'Not done'

        message = {
            "reason": reason
        }
        self.custom_logging.log(event='spider_closed', message=message)
        self.client.close()
    def errback_func(self, failure):
        self.custom_logging.log(event='failure', message=repr(failure))
        print(failure)
    def get_absolute_path(self, news_url):
        if news_url is None:
            return None

        if self.domain in news_url:
            return news_url

        return urllib.parse.urljoin(self.domain, news_url)

    def extract_id_from_url(self, news_url):
        pass

    def recognize_url(self, news_url):
        return 'test_url'

    def update_old_item(self, news_id, published_at):
        document = self.collection.find_one({"news_id": news_id})
        if document is None:
            return 0

        if published_at is None:
            return 2
        last_time_in_page = document.get("last_time_in_page", '')
        if last_time_in_page is not None and last_time_in_page.date() < published_at.date():
            try:
                self.collection.update_one({"_id": document["_id"]}, {"$set": {"last_time_in_page": published_at}})
            except Exception as e:
                message = f"Unable to update old item {news_id} because {e}"
                print(message)
                self.custom_logging.debug(message)
                return 1
        if last_time_in_page is not None and last_time_in_page < datetime.datetime.now() - datetime.timedelta(days=3):
            return 3
        return 2


    def generate_next_page(self, current_page):
       pass

    def check_spider_finished(self):
        if self.current_page is None:
            return False
        if 'end' in self.current_page and len(self.list_request) == 0:
            return True
        return False

    def get_full_news_id(self, news_id: str):
        if not news_id.startswith(self.spider_code):
            return self.spider_code + news_id



