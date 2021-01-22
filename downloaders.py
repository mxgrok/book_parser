import random
import traceback

import requests
import logging

import urllib3
from requests.structures import CaseInsensitiveDict

from exceptions import ProxiesPoolIsemptyExeption, ResponseRedirectException
from helpers import Helpers
from proxy import ProxiesPool
from storages.storage_abstract import StorageAbstract


logger = logging.getLogger()
logger.setLevel('DEBUG')


class BooksDownloader:

    def __init__(self, storage: StorageAbstract, redirected_codes: tuple, user_agents: list = None):
        self.redirected_codes: tuple = redirected_codes
        self.user_agents: list = user_agents
        self.storage: StorageAbstract = storage

    def get_user_agent(self) -> dict:
        if self.user_agents:
            return {'User-Agent': random.choice(self.user_agents)}

    def check_for_redirect(self, response: requests.Response):
        if response.status_code in self.redirected_codes:
            raise ResponseRedirectException

    def get_content(self, url: str, proxies: dict = None, timeout: int = 30) -> bytes:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        headers: CaseInsensitiveDict = requests.utils.default_headers()
        user_agent: dict = self.get_user_agent()
        if user_agent:
            headers.update(user_agent)

        response: requests.Response = requests.get(
            url,
            proxies=proxies,
            headers=headers,
            timeout=timeout,
            verify=False,
            allow_redirects=False
        )
        self.check_for_redirect(response)

        response.raise_for_status()

        return response.content

    def download_books_by_urls(self, urls: list):
        for url in urls:
            try:
                content: bytes = self.get_content(url)
            except Exception as _err:
                continue
            else:
                cleaned_url: str = Helpers.clean_url(url)
                filename: str = f'{cleaned_url}.txt'
                self.storage.save(content, filename)


class BooksDownloaderThroughProxy(BooksDownloader):

    def __init__(self, storage: StorageAbstract, proxies_pool: ProxiesPool, redirected_codes: tuple,
                 user_agents: list = None):
        super().__init__(storage, redirected_codes, user_agents)
        self.proxies_pool = proxies_pool

        self.current_proxy: dict = dict()

    def set_new_proxy(self):
        if self.current_proxy:
            return
        try:
            self.current_proxy: dict = self.proxies_pool.get().__next__()
        except StopIteration:
            raise ProxiesPoolIsemptyExeption('Proxies pool is empty')

    def reset_proxy(self):
        logger.info('Setting new proxy...')
        self.current_proxy = dict()
        self.set_new_proxy()

    def get_content_with_proxies_pool(self, url: str) -> bytes:
        while True:
            try:
                self.set_new_proxy()
                content: bytes = self.get_content(url, proxies=self.current_proxy)

            except requests.exceptions.ProxyError as _err:
                self.reset_proxy()
                continue
            else:
                return content

    def download_books_by_urls(self, urls: list):
        for url in urls:

            try:
                content = self.get_content_with_proxies_pool(url)
            except ProxiesPoolIsemptyExeption as _err:
                logger.error(f"Can't get new proxy: {_err}")
                break

            except ResponseRedirectException as _err:
                logger.error(f"Current page: {url} was redirected")
                continue

            except Exception as _err:
                error: str = ''.join(
                    traceback.TracebackException.from_exception(_err).format()
                )
                logger.error(error)
                break

            else:
                cleaned_url: str = Helpers.clean_url(url)
                filename: str = f'{cleaned_url}.txt'
                self.storage.save(content, filename)
