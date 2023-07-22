import scrapy
from bdscrawler.bdscrawler.settings import LOGGING_DATABASE, LOGGING_COLLECTION, ROOT_LOG_PATH
from bdscrawler.basecrawler.utils.helpers import *
import datetime
class BaseLogging:
    def __init__(self, spider):
        self.spider = spider
        self.name = spider.name
        self.collection = spider.client[LOGGING_DATABASE][LOGGING_COLLECTION]
        self.runtime_id = datetime.datetime.now()
        self.log_file_path = None

    def format_message(self, message):
        if isinstance(message, str):
            message = {'message': message}
        message['source'] = self.name
        message['createdAt'] = datetime.datetime.now()
        message['runtime_id'] = self.runtime_id
        return message

    def log(self, event, message):
        message = self.format_message(message)
        message['event'] = event
        self.collection.insert_one(message)

    def debug(self, message, event='debug'):
        if isinstance(message, dict):
            message['event'] = event
        if isinstance(message, str):
            message = {
                'message': message,
                'event': event
            }
        message = str(message)
        formatted_message = f"\n{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')};{message}"
        with open(self.log_file_path, "a") as log_file:
            log_file.write(formatted_message)

    def current(self, message):
        event = 'current'
        message = {
            'current_page': message
        }
        self.log(event='current', message=message)
    def request(self, request_url):
        event = 'request'
        message = {
            'request_url': request_url
        }
        self.log(event=event, message=message)

    def response(self, response_url):
        event = 'response'
        message = {
            'response_url': response_url
        }
        self.log(event=event, message=message)


    def init_log(self):
        spider_log_folder = os.path.join(ROOT_LOG_PATH, self.name)
        today_log_folder = os.path.join(spider_log_folder, get_today_string())
        file_name = get_runtime_string() + '.log'
        self.log_file_path = os.path.join(today_log_folder, file_name)
        create_folder(spider_log_folder)
        create_folder(today_log_folder)
        create_file(self.log_file_path)

    def load_runtime_before(self):
        pass






