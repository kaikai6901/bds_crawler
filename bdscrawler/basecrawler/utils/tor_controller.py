import logging
import random
import time
import requests
import configparser
from stem import Signal
from stem.control import Controller
from stem.util.log import get_logger
from bdscrawler.bdscrawler.settings import CONFIG_PATH, TOR_CONFIG_NAME, IP_CHECK_SERVICE, PRIVOXY_ENDPOINT_PATH
logger = get_logger()
logger.propagate = False

class TorController:
    def __init__(self, allow_reuse_ip_after: int = 20):
        self.allow_reuse_ip_after = allow_reuse_ip_after
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_PATH)
        # self.password = self.config.get(TOR_CONFIG_NAME, 'password')
        self.used_ips = list()
        self.proxy_list = self.read_config_proxy()
        self.counter = 0
        self.current_port = self.proxy_list[self.counter][1]
        self.current_proxy = self.proxy_list[self.counter][0]


    def get_current_proxy(self):
        self.current_port = self.proxy_list[self.counter][1]
        self.current_proxy = self.proxy_list[self.counter][0]
        self.counter = (self.counter + 1) % (len(self.proxy_list))
        print(self.counter)
        return self.current_proxy

    def read_config_proxy(self):
        with open(PRIVOXY_ENDPOINT_PATH, 'r') as file:
            proxy_config_list = file.read().splitlines()
        proxy_list = list()
        for proxy_config in proxy_config_list:
            if proxy_config.startswith('#'):
                continue

            proxy, control_port = proxy_config.split(',')
            control_port = int(control_port)
            proxy_list.append((proxy, control_port))

        return proxy_list
    def get_ip(self) -> str:
        """Returns the current IP used by Tor."""

        with requests.Session() as session:
            r = session.get(IP_CHECK_SERVICE, proxies={'http': self.current_proxy})

            if r.ok:
                session.close()
                return r.text.replace('\n', '')
            return r.text.replace('\n', '')

        return ''

    def change_ip(self) -> None:
        """Send IP change signal to Tor."""

        with Controller.from_port(port=self.current_port) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)

    def renew_ip(self) -> None:
        new_ip = None

        # Try to change the IP 10 times
        for _ in range(10):
            self.change_ip()

            new_ip = self.get_ip()

            # Waits for possible IP change
            waiting = 0
            while waiting <= 30:
                if new_ip in self.used_ips:
                    waiting += 2.5
                    time.sleep(2.5)

                    new_ip = self.get_ip()

                    if not new_ip:
                        break

                else:
                    break

            # If we can recover the IP, check if it has already been used
            if new_ip:

                # Controls IP reuse
                if self.allow_reuse_ip_after > 0:
                    if len(self.used_ips) == self.allow_reuse_ip_after:
                        del self.used_ips[0]
                    self.used_ips.append(new_ip)

                return new_ip

            # Wait a random time to try again
            time.sleep(random.randint(5, 30))

        # Could not change IP
        return ''

