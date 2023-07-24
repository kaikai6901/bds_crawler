import random
from bdscrawler.basecrawler.utils.helpers import *

class HomedyRandomHeaderGenerator:
    _list_referer = ['https://www.bing.com/', 'https://duckduckgo.com/', 'https://vn.search.yahoo.com/',
                     'https://www.google.com.vn/?hl=vi']

    _list_accept = ['application/json, text/javascript, */*; q=0.01', '*/*', 'application/json, text/javascript']
    _list_accept_language = ['vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5', 'en-US,en;q=0.5',
                             'vi-VN,vi;q=0.9,fr-FR;q=0.5', 'en-US,en;q=0.5;q=0.9,fr-FR', 'en-US,en;q=0.5;q=0.6,en', 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5']
    _list_accept_encoding = ['gzip, deflate, br', 'gzip, deflate', 'gzip, br']

    @staticmethod
    def generate_random_header():
        headers = {}
        headers['Accept-Encoding'] = random.choice(HomedyRandomHeaderGenerator._list_accept_encoding)
        headers['Accept-Language'] = random.choice(HomedyRandomHeaderGenerator._list_accept_language)
        headers['Accept'] = random.choice(HomedyRandomHeaderGenerator._list_accept)
        headers["Authority"] = "homedy.com"
        headers['Referer'] = random.choice(HomedyRandomHeaderGenerator._list_referer)
        headers["Sec-Fetch-Site"] = "same-origin"
        headers['Sec-Fetch-Dest'] = "empty"
        headers['Sec-Fetch-Mode'] = 'cors'
        return headers
