import config
from parsers.bs_parser_abstract import BsParserAbstract
from parsers.tululu_bs_parser import TululuBsParser
from downloaders.books_downloader_through_proxy import BooksDownloaderThroughProxy
from proxy import ProxiesPool
from storages.fs_storage import FileSystemStorage


if __name__ == '__main__':
    proxies_pool = ProxiesPool(config.proxies, 'https://api.ipify.org?format=json')
    storage = FileSystemStorage('C:\\Users\\mxgrok\\projects\\book_parser\\books')
    tululu_parser: BsParserAbstract = TululuBsParser()

    book_page_url_tpl = 'https://tululu.org/b{}/'
    book_page_urls = [book_page_url_tpl.format(i) for i in range(1, 11)]

    books_downloader = BooksDownloaderThroughProxy(
        storage,
        proxies_pool,
        config.redirected_codes,
        tululu_parser,
        config.user_agents
    )
    book_page_info_list = books_downloader.get_books_information(book_page_urls)
    print(book_page_info_list)
    books_downloader.download_books_by_urls(book_page_info_list)
