import random
import traceback
from logging import Logger
from urllib.parse import unquote

import requests

from requests.structures import CaseInsensitiveDict

from exceptions import ResponseRedirectException
from parsers.bs_parser_abstract import BsParserAbstract
from storages.storage_abstract import StorageAbstract


class Downloader:

    def __init__(self,
                 parser: BsParserAbstract,
                 logger: Logger,
                 user_agents: list = None,
                 redirected_codes: tuple = (301, 302)):
        self.logger = logger
        self.parser: BsParserAbstract = parser
        self.redirected_codes: tuple = redirected_codes
        self.user_agents: list = user_agents

    def get_user_agent(self) -> dict:
        if self.user_agents:
            return {'User-Agent': random.choice(self.user_agents)}

    def check_for_redirect(self, response: requests.Response):
        if response.status_code in self.redirected_codes:
            raise ResponseRedirectException

    def get_response(self, url: str, proxies: dict = None, timeout: int = 30) -> requests.Response:
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

    def download_books_by_urls(self, books: list, storage: StorageAbstract):
        for book in books:
            try:
                response: requests.Response = self.get_response(book.get('url'))
                content: bytes = response.content.decode(response.encoding).encode()

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
                content: bytes = self.get_content(image_url)

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

