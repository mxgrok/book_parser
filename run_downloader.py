import argparse
import json
import os
import uuid
from urllib.parse import urljoin, unquote, urlsplit
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
        title = soup.select_one('div#content h1').text.strip()
        title, author = [item.strip() for item in title.split('::')]
        download_book_link = soup.select_one('a:-soup-contains("скачать txt")').get('href')
        download_image_link = soup.select_one('div.bookimage a img')['src']

    if not download_book_link:
        raise BookDownloadLinkNotFound

    return {
        'title': title,
        'author': author,
        'image_url': urljoin(response.request.url, download_image_link) if download_image_link else None,
        'text': soup.select_one('table.d_book tr td').text,
        'comments': [item.contents[-1].text for item in soup.select('div.texts')],
        'genres': [item.text for item in soup.select('span.d_book a')],
        'url': urljoin(response.request.url, download_book_link)
    }


def download_and_save_book_to_fs(book_url, book_title, books_path):
    response = get_page(book_url)
    book_content: bytes = response.content.decode(response.encoding).encode()

    unique_part_of_name: str = str(uuid.uuid4())
    sanitized_book_name = sanitize_filename(book_title)
    book_file_name = f"{unique_part_of_name}--{sanitized_book_name}.txt"

    book_file_path: str = os.path.join(books_path, book_file_name)
    with open(book_file_path, 'wb') as file:
        file.write(book_content)

    return book_file_path


def download_and_save_book_image_to_fs(book_image_url, images_path):
    response = get_page(book_image_url)
    image_name = [_ for _ in unquote(urlsplit(book_image_url).path).split('/') if _][-1]

    unique_part_of_name: str = str(uuid.uuid4())
    sanitized_image_name = sanitize_filename(image_name)
    image_file_name = f"{unique_part_of_name}-{sanitized_image_name}"

    image_file_path: str = os.path.join(images_path, image_file_name)
    with open(image_file_path, 'wb') as file:
        file.write(response.content)

    return image_file_path


def write_book_information_into_json_file(json_path: str, book_information: dict):
    if not os.path.exists(json_path):
        with open(json_path, 'w', encoding='utf-8') as new_json_file:
            json.dump([], new_json_file, ensure_ascii=False)

    with open(json_path, 'r', encoding='utf-8') as json_file:
        current_data = json.load(json_file)

    with open(json_path, 'w', encoding='utf-8') as json_file:
        current_data.append(book_information)
        json.dump(current_data, json_file, indent=4, sort_keys=True, ensure_ascii=False)


def download_tululu(urls: list, images_path: str = 'images', books_path: str = 'books', json_file_path: str = 'book_info.json'):
    os.makedirs(images_path, exist_ok=True)
    os.makedirs(books_path, exist_ok=True)

    for url in urls:

        try:
            page_response = get_page(url)
            book = parse_book_page(page_response)
            book_information = {_: __ for _, __ in book.items() if _ not in ('url', 'image_url')}
            book_url, book_title, book_image_url = (
                book[book_property_key] for book_property_key in ('url', 'title', 'image_url')
            )

            book_information.update({
                'book_path': download_and_save_book_to_fs(book_url, book_title, books_path),
                'img_src': download_and_save_book_image_to_fs(book_image_url, images_path) if book_image_url else None
            })

            write_book_information_into_json_file(json_file_path, book_information)

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

    disable_warnings(InsecureRequestWarning)

    tululu_urls_generation_template: str = 'https://tululu.org/b{}/'
    page_urls = generate_urls(tululu_urls_generation_template, args.start_id, args.end_id)

    download_tululu(page_urls)
