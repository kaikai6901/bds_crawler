from scrapy.exceptions import NotConfigured
from bdscrawler.bdscrawler.utils.AlonhadatHelpers import AlonhadatRandomHeaderGenerator
from bdscrawler.basecrawler.utils.helpers import *
from scrapy.downloadermiddlewares.redirect import BaseRedirectMiddleware, _build_redirect_request
from bdscrawler.basecrawler.utils.tor_controller import TorController
from urllib.parse import urljoin, urlparse
from w3lib.url import safe_url_string
import time

class CustomRedirectMiddleware(BaseRedirectMiddleware):
    enabled_setting = "CUSTOM_REDIRECT_ENABLED"

    def __init__(self, settings):
        if not settings.getbool(self.enabled_setting):
            raise NotConfigured

        self.max_redirect_times = settings.getint("REDIRECT_MAX_TIMES")
        self.priority_adjust = settings.getint("REDIRECT_PRIORITY_ADJUST")

    @classmethod
    def from_crawler(cls, crawler):
        return cls( crawler.settings)

    def process_response(self, request, response, spider):
        if (
                request.meta.get("dont_redirect", False)
                or response.status in getattr(spider, "handle_httpstatus_list", [])
                or response.status in request.meta.get("handle_httpstatus_list", [])
                or request.meta.get("handle_httpstatus_all", False)
        ):
            return response

        allowed_status = (301, 302, 303, 307, 308)
        if "Location" not in response.headers or response.status not in allowed_status:
            return response

        location = safe_url_string(response.headers["Location"])
        if response.headers["Location"].startswith(b"//"):
            request_scheme = urlparse(request.url).scheme
            location = request_scheme + "://" + location.lstrip("/")

        redirected_url = urljoin(request.url, location)

        if response.status == 302 and 'xac-thuc-nguoi-dung' in redirected_url:
            spider.log('Redirect Middleware')
            retry_number = request.meta.get('retry_number', 0)
            if retry_number <= self.max_redirect_times:
                # change here
                # new_ip = spider.tor_controller.renew_ip()
                # if not new_ip:
                #     raise Exception('FatalError: Failed to find a new IP')
                # spider.log(f'New Tor IP: {new_ip}')
                # time.sleep(self.delay_redirect * (retry_number + 1))
                # return response
                request.meta['retry_number'] = retry_number + 1
                request.priority = request.priority + self.priority_adjust
                return request
            else:
                # raise RedirectedAuthenException(request.url)
                pass
        if response.status in (301, 307, 308) or request.method == "HEAD":
            redirected = _build_redirect_request(request, url=redirected_url)
            return self._redirect(redirected, request, spider, response.status)

        redirected = self._redirect_request_using_get(request, redirected_url)
        return self._redirect(redirected, request, spider, response.status)

class CustomHeadersMiddleware(object):

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('CUSTOM_HEADER_ENABLED', False):
            raise NotConfigured()
        mw = cls()
        return mw


    def process_request(self, request, spider):
        proxy = request.meta['proxy']
        headers = AlonhadatRandomHeaderGenerator.generate_random_header(proxy)

        for header, value in headers.items():
            request.headers[header] = value
