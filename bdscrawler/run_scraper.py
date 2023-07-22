from bdscrawler.bdscrawler.spiders.test_spider import QuotesSpider
from bdscrawler.bdscrawler.spiders.bds123_spider import BDS123Spider
from bdscrawler.bdscrawler.spiders.alonhadat_spider import AlonhadatSpider
from bdscrawler.bdscrawler.spiders.homedy_spider import HomedySpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os

class Scraper:
    def __init__(self, ignore_runtime_before=True, ignore_old_request=True):
        setting_file_path = 'bdscrawler.bdscrawler.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', setting_file_path)
        self.ignore_runtime_before = ignore_runtime_before
        self.ignore_old_request = ignore_old_request
        self.process = CrawlerProcess(get_project_settings())
        self.spider = HomedySpider

    def run_spiders(self):
        self.process.crawl(self.spider, ignore_runtime_before=self.ignore_runtime_before, ignore_old_request=self.ignore_old_request)
        self.process.start()