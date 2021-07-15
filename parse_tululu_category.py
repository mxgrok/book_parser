from contextlib import suppress
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from run_downloader import raise_if_redirect, get_page


def get_next_page_url(response):
    soup: BeautifulSoup = BeautifulSoup(response.text, 'lxml')

    with suppress(Exception):
        next_page = urljoin(response.request.url, soup.find('span', class_='npage_select').next_sibling['href'])
        return next_page


def parse_category_page(response):
    soup: BeautifulSoup = BeautifulSoup(response.text, 'lxml')
    with suppress(Exception):
        books_urls = set([
            urljoin(response.request.url, book_item.find('a')['href'])
            for book_item in soup.find_all('div', class_='bookimage')
        ])

        return books_urls


def download_tululu_by_category(url):
    current_url = url

    books_counter = 0

    while True:
        response = get_page(current_url)
        books_urls = parse_category_page(response)
        current_url = get_next_page_url(response)

        if not current_url:
            break

        books_counter += len(books_urls)
        print(books_counter, books_urls)


if __name__ == '__main__':
    disable_warnings(InsecureRequestWarning)
    category_url = 'https://tululu.org/l55'
    download_tululu_by_category(category_url)
