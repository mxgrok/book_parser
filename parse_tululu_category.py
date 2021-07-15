import os
import time
from contextlib import suppress
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from exceptions import ResponseRedirectException
from run_downloader import get_page, download_tululu


def get_next_page_url(response):
    soup: BeautifulSoup = BeautifulSoup(response.text, 'lxml')

    with suppress(Exception):
        next_page = urljoin(response.request.url, soup.select_one('span.npage_select').nextSibling['href'])
        return next_page


def parse_category_page(response):
    soup: BeautifulSoup = BeautifulSoup(response.text, 'lxml')
    with suppress(Exception):
        books_urls = list(set([
            urljoin(response.request.url, book_item.select_one('a')['href'])
            for book_item in soup.select('div.bookimage')
        ]))

        return books_urls


def download_tululu_by_category(url, images_path, books_path, limit=None):
    current_url = url

    books_counter = 0

    while True:
        try:
            response = get_page(current_url)
        except ResponseRedirectException:
            continue
        books_urls = parse_category_page(response)
        current_url = get_next_page_url(response)

        if not current_url:
            break
        if limit and books_counter >= limit:
            break

        books_counter += len(books_urls)
        print(books_counter, books_urls)
        download_tululu(books_urls, images_path, books_path)


if __name__ == '__main__':
    disable_warnings(InsecureRequestWarning)
    category_url = 'https://tululu.org/l55/'
    books_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'books')
    images_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'images')
    download_tululu_by_category(category_url, images_path, books_path, limit=100)
