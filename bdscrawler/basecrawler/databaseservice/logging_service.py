
from bdscrawler.basecrawler.logs.BaseLogging import BaseLogging

class LoggingDatabaseService:
    def __init__(self, custom_logging: BaseLogging):
        self.custom_logging = custom_logging
        self.name = custom_logging.name
        self.collection = custom_logging.collection

    def read_log(self):
        latest_doc = self.collection.find_one(
            {'source': self.name},
            sort=[('runtime_id', -1), ('createdAt', -1)]
        )

        if latest_doc:
            latest_runtime_id = latest_doc['runtime_id']
            spider_closed = self.collection.find_one(
                {'source': self.name,
                 'runtime_id': latest_runtime_id,
                 'event': 'spider_closed'}
            )
            if spider_closed:
                reason = spider_closed
                if 'finished' in reason:
                    return None, list()

            latest_current_page = self.collection.find_one(
                {'source': self.name,
                 'event': 'current',
                 'runtime_id': latest_runtime_id},
                 sort=[('createdAt', -1)]
            )
            if latest_current_page:
                current_page = latest_current_page['current_page']
            else:
                current_page = None

            request_urls = [
                doc['request_url'] for doc in self.collection.find(
                    {'source': self.name, 'event': 'request', 'runtime_id': latest_runtime_id}
                )
            ]

            response_urls = [
                doc['response_url'] for doc in self.collection.find(
                    {'source': self.name, 'event': 'response', 'runtime_id': latest_runtime_id}
                )
            ]

            list_request = list(set(request_urls) - set(response_urls))
            self.custom_logging.current(current_page)
            for request_url in list_request:
                self.custom_logging.request(request_url)
            return current_page, list_request

        return None, list()



