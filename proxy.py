from logging import Logger

import requests
import urllib3


class Proxy:

    def __init__(self,
                 proxy: str,
                 logger: Logger,
                 check_by_url: str = None,
                 proxy_types: tuple = ('http', 'https')):
        self.proxy: str = proxy
        self.proxy_types: tuple = proxy_types
        self.check_by_url: str = check_by_url
        self.logger = logger

    def is_valid(self, proxies: dict, check_by_url: str) -> bool:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            requests.get(check_by_url, proxies=proxies, timeout=1, verify=False)
        except (requests.exceptions.ProxyError, requests.exceptions.ConnectTimeout):
            self.logger.debug(f'Not valid proxy: {proxies}')
        else:
            return True

        return False

    def set(self):
        proxies: dict = {
            type: f'{type}://{self.proxy}' for type in self.proxy_types
        }
        if self.check_by_url:
            if not self.is_valid(proxies, self.check_by_url):
                return

        return proxies


class ProxiesPool:

    def __init__(self,
                 proxies_list: list,
                 logger: Logger,
                 check_by_url: str = None,
                 proxy_types: tuple = ('http', 'https')):
        self.proxy_types: tuple = proxy_types
        self.check_by_url: str = check_by_url
        self.proxies_list: list = proxies_list
        self.proxies_pool: list = []
        self.logger = logger

    def get(self):
        for item in self.proxies_list:
            proxy_object: dict = Proxy(item, self.logger, self.check_by_url, self.proxy_types).set()
            if proxy_object:
                yield proxy_object

            continue
