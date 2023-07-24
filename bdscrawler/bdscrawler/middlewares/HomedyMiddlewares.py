from bdscrawler.bdscrawler.utils.HomedyHelpers import HomedyRandomHeaderGenerator
from scrapy.exceptions import NotConfigured

class CustomHeadersMiddleware(object):

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('CUSTOM_HEADER_ENABLED', False):
            raise NotConfigured()
        mw = cls()
        return mw

    def process_request(self, request, spider):
        headers = HomedyRandomHeaderGenerator.generate_random_header()

        for header, value in headers.items():
            request.headers[header] = value

