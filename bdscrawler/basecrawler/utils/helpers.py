import datetime
import os
import random

from unidecode import unidecode
import re
from bdscrawler.bdscrawler.settings import *
def get_today_string():
    today = datetime.date.today()
    today_string = today.strftime("%Y-%m-%d")
    return today_string
    # return '2023-06-27'
def get_runtime_string():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def create_folder(path):
    if os.path.exists(path):
        print(f'Log folder {path} already exists')
    else:
        # Create the folder
        os.makedirs(path)
        print(f"Folder '{path}' created successfully.")

def create_file(path):
    if os.path.exists(path):
        print(f"Log file '{path}' already exists.")
    else:
        # Create the log file
        with open(path, "w") as log_file:
            log_file.write("")
        print(f"Log file '{path}' created successfully.")

def parse_headers(headers):
    headers_dict = {key.decode(): value.decode() for key, value in headers.items()}
    return headers_dict

def convert_time(t: str):
    if not t:
        return None
    t = unidecode(t).strip().lower()
    t = t.replace('ngay dang: ', '').strip()

    formats = ['%d/%m/%Y', '%H:%M %d/%m/%Y']

    for format in formats:
        try:
            formatted_time = datetime.datetime.strptime(t, format)
            return formatted_time
        except:
            pass
    if "gio truoc" in t:
        hours = int(t.split(' ')[0])
        delta = datetime.timedelta(hours=hours)
    elif "ngay truoc" in t:
        days = int(t.split()[0])
        delta = datetime.timedelta(days=days)
    elif 'hom nay' in t:
        return datetime.datetime.now()
    elif 'hom qua' in t:
        return datetime.datetime.now() - datetime.timedelta(days=1)
    elif 'phut truoc' in t:
        minutes = int(t.split(' ')[0])
        delta = datetime.timedelta(minutes=minutes)
    else:
        raise ValueError('Not handle this datetime format')

    current_time = datetime.datetime.now()
    converted_time = current_time - delta

    return converted_time

def extract_float_number(string):
    string = string.strip()
    pattern = r"[-+]?\d*\.\d+|\d+"
    matches = re.findall(pattern, string)
    if len(matches) > 0:
        return float(matches[0])
    else:
        return None

def extract_words_with_numbers_and_remaining(sentence):
    pattern = r'(\b\w*\d\w*\b)(.*)'
    match = re.match(pattern, sentence)
    if match:
        words_with_numbers = match.group(1)
        remaining = match.group(2).strip()
        return words_with_numbers, remaining
    else:
        return '', ''

def get_format_string(s: str):
    if s is None:
        return None
    if not isinstance(s, str):
        return None
    return unidecode(s).strip().lower()

def convert_price_unit(unit: str):
    if unit is None:
        return None
    if not isinstance(unit, str):
        return None
    unit = get_format_string(unit)

    if 'trieu' in unit:
        return 1e6
    elif 'ty' in unit:
        return 1e9
    elif 'nghin' in unit:
        return 1e3

    return 1

class ProxyManager:
    _list_proxies = None
    _counter = 0
    _previous_proxy = None
    _max_counter = 3
    @staticmethod
    def read_proxy_list(_config_path):
        with open(_config_path, 'r') as file:
            proxy_list = file.read().splitlines()
        ProxyManager._list_proxies = proxy_list

    @staticmethod
    def get_random_proxy():
        if not ProxyManager._list_proxies:
            ProxyManager.read_proxy_list(PRIVOXY_ENDPOINT_PATH)
        # Shuffle the proxy list if all proxies have been returned
        proxy = random.choice(ProxyManager._list_proxies)
        if ProxyManager._counter > ProxyManager._max_counter and proxy == ProxyManager._previous_proxy:
            proxy = ProxyManager.get_random_proxy()  # Recursively call until a different proxy is found
        if proxy != ProxyManager._previous_proxy:
            ProxyManager._counter = 0
        ProxyManager._previous_proxy = proxy
        ProxyManager._counter += 1
        return proxy, ProxyManager._counter

