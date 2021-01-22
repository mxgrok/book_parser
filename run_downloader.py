import config
from downloaders import BooksDownloaderThroughProxy
from proxy import ProxiesPool
from storages.fs_storage import FileSystemStorage


if __name__ == '__main__':
    proxies_pool = ProxiesPool(config.proxies, 'https://api.ipify.org?format=json')
    storage = FileSystemStorage('C:\\Users\\mxgrok\\projects\\book_parser\\books')

    book_url_tpl = 'https://tululu.org/txt.php?id={}'
    book_urls = [book_url_tpl.format(i) for i in range(1, 11)]

    books_downloader = BooksDownloaderThroughProxy(storage, proxies_pool, config.redirected_codes, config.user_agents)
    books_downloader.download_books_by_urls(book_urls)
