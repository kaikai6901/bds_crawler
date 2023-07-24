from bdscrawler.basecrawler.utils.tor_controller import TorController
from scrapy.exceptions import NotConfigured
from bdscrawler.bdscrawler.settings import PRIVOXY_ENDPOINT
from bdscrawler.basecrawler.utils.helpers import *
class TorProxyMiddleware(object):
    def __init__(self, max_count: int = 5):
        self.items_scraped = {}
        self.max_count = max_count


    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('TOR_IPROTATOR_ENABLED', False):
            raise NotConfigured()
        max_count = crawler.settings.getint('TOR_IPROTATOR_CHANGE_AFTER', 5)

        mw = cls(max_count=max_count)
        return mw

    def process_request(self, request, spider):
        proxy = spider.tor_controller.get_current_proxy()
        if proxy not in self.items_scraped:
            self.items_scraped[proxy] = 0
        if self.items_scraped[proxy] > self.max_count or spider.number_error > 0:
            spider.log('Changing Tor IP...')
            self.items_scraped[proxy] = 0

            new_ip = spider.tor_controller.renew_ip()
            if not new_ip:
                raise Exception('FatalError: Failed to find a new IP')
            spider.log(f'New Tor IP: {new_ip}')

        # spider.log(f'Current Ip is: {spider.tor_controller.get_ip()}')

        if 'proxy' in request.meta:
            if request.meta['proxy'] is not None:
                proxy = request.meta['proxy']
        spider.log(proxy)
        request.meta['proxy'] = proxy
        self.items_scraped[proxy] += 1
