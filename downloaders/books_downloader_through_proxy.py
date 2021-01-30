import traceback
from logging import Logger
from urllib.parse import unquote

import requests

from downloaders.books_downloader import Downloader
from exceptions import ProxiesPoolIsemptyExeption, ResponseRedirectException
from parsers.bs_parser_abstract import BsParserAbstract
from proxy import ProxiesPool
from storages.storage_abstract import StorageAbstract


class DownloaderThroughProxy(Downloader):

    def __init__(self, proxies_pool: ProxiesPool, redirected_codes: tuple,
                 parser: BsParserAbstract,
                 logger: Logger,
                 user_agents: list = None):
        super().__init__(redirected_codes, parser, logger, user_agents)
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
        self.logger.info('Setting new proxy...')
        self.current_proxy = dict()
        self.set_new_proxy()

    def get_response_with_proxies_pool(self, url: str) -> requests.Response:
        while True:
            try:
                self.set_new_proxy()
                response: requests.Response = self.get_response(url, proxies=self.current_proxy)

            except requests.exceptions.ProxyError as _err:
                self.reset_proxy()
                continue
            else:
                return response

    def get_content_by_url(self, url) -> bytes:

        content: bytes = self.get_response_with_proxies_pool(url).content
        return content

    def download_books_by_urls(self, books: list, storage: StorageAbstract):
        for book in books:
            try:
                content: bytes = self.get_content_by_url(book.get('url'))
            except ProxiesPoolIsemptyExeption as _err:
                self.logger.error(f"Can't get new proxy: {_err}")
                break

            except ResponseRedirectException as _err:
                self.logger.error(f"Current page: {book.get('url')} was redirected")
                continue

            except Exception as _err:
                error: str = ''.join(
                    traceback.TracebackException.from_exception(_err).format()
                )
                self.logger.error(error)
                continue

            else:
                book_name: str = book.get('title')
                filename: str = f'{book_name}.txt'
                storage.save(content, filename)

    def download_images_by_urls(self, images_url: list, storage: StorageAbstract):
        for image_url in images_url:
            try:
                content: bytes = self.get_content_by_url(image_url)
            except ProxiesPoolIsemptyExeption as _err:
                self.logger.error(f"Can't get new proxy: {_err}")
                break

            except ResponseRedirectException as _err:
                self.logger.error(f"Current page: {image_url} was redirected")
                continue

            except Exception as _err:
                error: str = ''.join(
                    traceback.TracebackException.from_exception(_err).format()
                )
                self.logger.error(error)
                continue

            else:
                image_name: str = [i for i in unquote(image_url).split('/') if i][-1]
                storage.save(content, image_name)

    def get_books_information(self, urls: list) -> list:
        books_information: list = []
        for url in urls:
            try:
                content: requests.Response = self.get_response_with_proxies_pool(url)
                book_information: dict = self.parser.parse(content.text, url)

            except Exception as _err:
                continue
            else:
                books_information.append(book_information)

        return books_information
