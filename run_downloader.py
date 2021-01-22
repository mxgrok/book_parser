from downloaders import BooksDownloaderThroughProxy
from proxy import ProxiesPool
from storages.fs_storage import FileSystemStorage

if __name__ == '__main__':

    # valid_proxies = check_proxy(proxies)
    valid_proxies = [
        '84.17.51.209:3128', '84.17.51.213:3128', '176.9.85.13:3128', '84.17.51.210:3128',
        '62.171.144.29:3128', '178.128.50.52:3128', '84.17.51.219:3128', '89.249.67.57:3128',
        '217.6.21.174:8080', '217.6.21.170:8080', '37.223.42.143:80'
    ]
    proxies_pool = ProxiesPool(valid_proxies, 'https://api.ipify.org?format=json')
    storage = FileSystemStorage('C:\\Users\\mxgrok\\projects\\book_parser\\books')

    book_url_tpl = 'https://tululu.org/txt.php?id={}'
    book_urls = [book_url_tpl.format(i) for i in range(1, 11)]

    books_downloader = BooksDownloaderThroughProxy(storage, proxies_pool)
    books_downloader.download_books_by_urls(book_urls)
