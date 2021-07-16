import os
from contextlib import suppress
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from exceptions import ResponseRedirectException
from run_downloader import get_page, download_tululu, parse_params


# FIXME: need to remove
def get_next_page_url_bs_parse(response):
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


def get_new_generated_page_url(start_page_number, end_page_number, url_category_tpl):
    def generate_page_iterator():
        for page_number in range(start_page_number, end_page_number):
            yield url_category_tpl.format(page_number)

    return generate_page_iterator


def download_tululu_by_category(page_url_generator, images_path, books_path, json_file_path, skip_images, skip_text):
    for page_url in page_url_generator():
        print(f'Current page url: {page_url}')
        try:
            response = get_page(page_url)
        except ResponseRedirectException:
            continue

        books_urls = parse_category_page(response)
        download_tululu(
            books_urls,
            images_path=images_path,
            books_path=books_path,
            json_file_path=json_file_path,
            skip_images=skip_images,
            skip_text=skip_text
        )


if __name__ == '__main__':
    args = parse_params()

    disable_warnings(InsecureRequestWarning)
    category_page_generation_template = 'https://tululu.org/l55/{}/'
    page_generator = get_new_generated_page_url(args.start_page, args.end_page, category_page_generation_template)

    destination_directory_path = args.dest_folder or os.path.abspath(os.path.dirname(__file__))
    books_path = os.path.join(destination_directory_path, 'books')
    images_path = os.path.join(destination_directory_path, 'images')

    json_file_path = args.json_path or os.path.join(destination_directory_path, 'book_info.json')

    download_tululu_by_category(
        page_generator,
        images_path=images_path,
        books_path=books_path,
        json_file_path=json_file_path,
        skip_images=args.skip_imgs,
        skip_text=args.skip_txt
    )
