import traceback

import requests
import logging

from downloaders.books_downloader import BooksDownloader
from exceptions import ProxiesPoolIsemptyExeption, ResponseRedirectException
from parsers.bs_parser_abstract import BsParserAbstract
from proxy import ProxiesPool
from storages.storage_abstract import StorageAbstract


logger = logging.getLogger()
logger.setLevel('DEBUG')


class BooksDownloaderThroughProxy(BooksDownloader):

    def __init__(self, storage: StorageAbstract, proxies_pool: ProxiesPool, redirected_codes: tuple,
                 parser: BsParserAbstract,
                 user_agents: list = None):
        super().__init__(storage, redirected_codes, parser, user_agents)
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

    def get_book_content_by_url(self, url) -> bytes:

        content: bytes = self.get_response_with_proxies_pool(url).content
        return content

    def download_books_by_urls(self, books: list):
        for book in books:
            try:
                content: bytes = self.get_book_content_by_url(book.get('url'))
            except ProxiesPoolIsemptyExeption as _err:
                logger.error(f"Can't get new proxy: {_err}")
                break

            except ResponseRedirectException as _err:
                logger.error(f"Current page: {book.get('url')} was redirected")
                continue

            except Exception as _err:
                error: str = ''.join(
                    traceback.TracebackException.from_exception(_err).format()
                )
                logger.error(error)
                break

            else:
                book_name: str = book.get('title')
                filename: str = f'{book_name}.txt'
                self.storage.save(content, filename)

    def get_books_information(self, urls:list) -> list:
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
