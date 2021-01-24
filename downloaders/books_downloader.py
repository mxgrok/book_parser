import random
import traceback

import requests
import logging

import urllib3
from requests.structures import CaseInsensitiveDict

from exceptions import ResponseRedirectException
from parsers.bs_parser_abstract import BsParserAbstract
from storages.storage_abstract import StorageAbstract


logger = logging.getLogger()
logger.setLevel('DEBUG')


class BooksDownloader:

    def __init__(self, storage: StorageAbstract, redirected_codes: tuple, parser: BsParserAbstract,
                 user_agents: list = None):
        self.parser: BsParserAbstract = parser
        self.redirected_codes: tuple = redirected_codes
        self.user_agents: list = user_agents
        self.storage: StorageAbstract = storage

    def get_user_agent(self) -> dict:
        if self.user_agents:
            return {'User-Agent': random.choice(self.user_agents)}

    def check_for_redirect(self, response: requests.Response):
        if response.status_code in self.redirected_codes:
            raise ResponseRedirectException

    def get_response(self, url: str, proxies: dict = None, timeout: int = 30) -> requests.Response:
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

        return response

    def get_content(self, url: str, proxies: dict = None, timeout: int = 30) -> bytes:
        response: requests.Response = self.get_response(url, proxies, timeout)

        return response.content

    def get_book_content_by_url(self, url) -> bytes:

        content: bytes = self.get_response(url).content
        return content

    def download_books_by_urls(self, books: list):
        for book in books:
            try:
                content: bytes = self.get_book_content_by_url(book.get('url'))

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
                content: requests.Response = self.get_response(url)
                book_information: dict = self.parser.parse(content.text, url)

            except Exception as _err:
                continue
            else:
                books_information.append(book_information)

        return books_information

