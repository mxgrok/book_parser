import argparse
import os
import uuid
from urllib.parse import urljoin, unquote
from contextlib import suppress

from pathvalidate import sanitize_filename
import requests
from bs4 import BeautifulSoup
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from exceptions import BookDownloadLinkNotFound, ResponseRedirectException


def get_page(url):
    response = requests.get(url, verify=False, allow_redirects=False)
    response.raise_for_status()
    raise_if_redirect(response)

    return response


def raise_if_redirect(response):
    if response.status_code not in (301, 302):
        return
    raise ResponseRedirectException


def parse_book_page(response):
    soup: BeautifulSoup = BeautifulSoup(response.text, 'lxml')
    download_book_link, download_image_link = None, None
    with suppress(Exception):
        title = soup.find('div', id='content').find('h1').text.strip()
        title, author = [item.strip() for item in title.split('::')]
        download_book_link = soup.select_one('a:-soup-contains("скачать txt")').get('href')
        download_image_link = soup.find('div', class_='bookimage').find('a').find('img')['src']

    if not download_book_link:
        raise BookDownloadLinkNotFound

    return {
        'title': title,
        'author': author,
        'image_url': urljoin(response.request.url, download_image_link) if download_image_link else None,
        'text': soup.findAll('table', class_='d_book')[1].find('tr').find('td').text,
        'comments': [item.contents[-1].text for item in soup.find_all('div', class_="texts")],
        'genres': [item.text for item in soup.find_all('a', title=lambda x: x and 'перейти к книгам этого жанра' in x)],
        'url': urljoin(response.request.url, download_book_link)
    }


def download_and_save_book_to_fs(book_info, books_path):
    response = get_page(book_info['url'])
    book_content: bytes = response.content.decode(response.encoding).encode()

    unique: str = str(uuid.uuid4())
    sanitized_book_name = sanitize_filename(book_info['title'])
    book_file_name = f"{unique}--{sanitized_book_name}.txt"

    book_file_path: str = os.path.join(books_path, book_file_name)
    with open(book_file_path, 'wb') as file:
        file.write(book_content)


def download_and_save_book_image_to_fs(book_info, images_path):
    if not book_info.get('image_url'):
        return

    response = get_page(book_info['image_url'])
    image_name = [_ for _ in unquote(book_info['image_url']).split('/') if _][-1]

    unique: str = str(uuid.uuid4())
    sanitized_book_name = sanitize_filename(image_name)
    image_file_name = f"{unique}-{sanitized_book_name}"

    image_file_path: str = os.path.join(images_path, image_file_name)
    with open(image_file_path, 'wb') as file:
        file.write(response.content)


def run_tululu_downloader(urls: list, images_path: str = 'images', books_path: str = 'books'):
    disable_warnings(InsecureRequestWarning)
    os.makedirs(images_path, exist_ok=True)
    os.makedirs(books_path, exist_ok=True)

    for url in urls:

        try:
            page_response = get_page(url)
            book_info = parse_book_page(page_response)
            download_and_save_book_to_fs(book_info, books_path)
            download_and_save_book_image_to_fs(book_info, images_path)
        except ResponseRedirectException:
            print(f'Detected redirect with request to page: {url}')
        except BookDownloadLinkNotFound:
            print(f'Link for downloading book not found on page: {url}')


def generate_urls(template: str, start_value: int, end_value: int) -> list:
    if end_value < start_value:
        raise ValueError(f"End id must be greater than start id")

    end_value += 1
    urls: list = [template.format(i) for i in range(start_value, end_value)]

    return urls


def parse_params() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--start_id", default='1', type=int,
        help="Setting start value for url generation, default = 1"
    )
    parser.add_argument(
        "-e", "--end_id",
        default='10', type=int,
        help="Setting start value for url generation, default is 10. End id must be greater than start id!"
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_params()

    generation_template: str = 'https://tululu.org/b{}/'
    page_urls = generate_urls(generation_template, args.start_id, args.end_id)

    run_tululu_downloader(page_urls)
