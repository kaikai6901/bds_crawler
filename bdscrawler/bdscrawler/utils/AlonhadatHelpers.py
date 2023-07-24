import random
from bdscrawler.basecrawler.utils.helpers import *

class AlonhadatRandomHeaderGenerator:
    _list_referer = ['https://www.bing.com/', 'https://duckduckgo.com/', 'https://vn.search.yahoo.com/',
                     'https://www.google.com.vn/?hl=vi']
    _list_accept_encoding = ['gzip, deflate, br', 'gzip, deflate', 'gzip, br']
    _list_accept_language = ['vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5', 'en-US,en;q=0.5',
                             'vi-VN,vi;q=0.9,fr-FR;q=0.5', 'en-US,en;q=0.5;q=0.9,fr-FR', 'en-US,en;q=0.5;q=0.6,en']


    @staticmethod
    def generate_random_header():
        headers = {}
        headers['Accept-Encoding'] = random.choice(AlonhadatRandomHeaderGenerator._list_accept_encoding)
        headers['Accept-Language'] = random.choice(AlonhadatRandomHeaderGenerator._list_accept_language)
        headers["Authority"] = "alonhadat.com.vn"
        headers["Accept"] = "*/*"
        # headers['Accept'] = random.choice(BDS123RandomHeaderGenerator._list_accept)
        # headers['Accept-Encoding'] = random.choice(BDS123RandomHeaderGenerator._list_accept_encoding)
        # headers['Accept-Language'] = random.choice(BDS123RandomHeaderGenerator._list_accept_language)
        # headers['Content-Type'] = 'application/json'
        headers["Origin"] = "https://alonhadat.com.vn"
        headers['Referer'] = random.choice(AlonhadatRandomHeaderGenerator._list_referer)
        headers["Sec-Fetch-Site"] = "same-origin"
        headers['Sec-Fetch-Dest'] = "empty"
        headers['Sec-Fetch-Mode'] = 'cors'
        return headers