import argparse

import config
from downloaders.books_downloader import Downloader
from parsers.bs_parser_abstract import BsParserAbstract
from parsers.tululu_bs_parser import TululuBsParser
from downloaders.books_downloader_through_proxy import DownloaderThroughProxy
from proxy import ProxiesPool
from storages.fs_storage import FileSystemStorage
from storages.storage_abstract import StorageAbstract


def run_downloader(downloader: Downloader, page_urls: list, images_path: str, books_path: str):
    books_storage: StorageAbstract = FileSystemStorage(books_path)
    image_storage: StorageAbstract = FileSystemStorage(images_path)
    book_pages_info: list = downloader.get_books_information(page_urls)

    print(book_pages_info)

    downloader.download_books_by_urls(book_pages_info, books_storage)
    img_urls: list = [i.get('image_url') for i in book_pages_info if i.get('image_url')]
    downloader.download_images_by_urls(img_urls, image_storage)


def generate_urls(template: str, start_value: int, end_value: int) -> list:
    if end_value < start_value:
        raise ValueError (f"End id must be greater than start id")

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
    parser.add_argument(
        "-p", "--use_proxy", type=bool,
        help="If you want to use proxies set proxies list in config file"
    )
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = parse_params()
    tululu_parser: BsParserAbstract = TululuBsParser()

    if args.use_proxy and hasattr(config, 'proxies'):
        proxies_pool = ProxiesPool(config.proxies, config.proxy_verifing_url)

        downloader = DownloaderThroughProxy(
            proxies_pool,
            config.redirected_codes,
            tululu_parser,
            config.user_agents
        )
    else:
        downloader = Downloader(
            config.redirected_codes,
            tululu_parser,
            config.user_agents
        )

    if not all((hasattr(config, 'images_path'), hasattr(config, 'books_path'))) \
            or not all((config.images_path, config.books_path)):
        raise ValueError("You must setting paths in config file")

    generation_template: str = 'https://tululu.org/b{}/'
    page_urls = generate_urls(generation_template, args.start_id, args.end_id)
    run_downloader(downloader, page_urls, config.images_path, config.books_path)
