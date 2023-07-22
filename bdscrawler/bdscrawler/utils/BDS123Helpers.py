import datetime
from unidecode import unidecode
import random

class BDS123RandomHeaderGenerator:
    _list_accept_encoding = ['gzip, deflate, br', 'gzip, deflate', 'gzip, br']
    _list_accept_language = ['vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5', 'en-US,en;q=0.5',
                             'vi-VN,vi;q=0.9,fr-FR;q=0.5', 'en-US,en;q=0.5;q=0.9,fr-FR', 'en-US,en;q=0.5;q=0.6,en']
    _list_referer = ['https://www.bing.com/', 'https://duckduckgo.com/', 'https://vn.search.yahoo.com/',
                     'https://www.google.com.vn/?hl=vi']
    _list_accept = ['application/json, text/plain, */*', 'application/json', '*/*']
    @staticmethod
    def generate_random_header():
        headers = {}
        headers['Authority'] = 'bds123.vn'
        # headers['Accept'] = random.choice(BDS123RandomHeaderGenerator._list_accept)
        # headers['Accept-Encoding'] = random.choice(BDS123RandomHeaderGenerator._list_accept_encoding)
        # headers['Accept-Language'] = random.choice(BDS123RandomHeaderGenerator._list_accept_language)
        # headers['Content-Type'] = 'application/json'
        headers['Origin'] = 'https://bds123.vn'
        headers['Referer'] = random.choice(BDS123RandomHeaderGenerator._list_referer)
        headers['Sec-Fetch-Dest'] = 'empty'
        headers['Sec-Fetch-Mode'] = 'cors'
        headers['Sec-Fetch-Site'] = 'same-origin'
        return headers