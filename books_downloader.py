import os
import traceback

import requests
import logging

import urllib3

logger = logging.getLogger()
logger.setLevel('DEBUG')


def get_content(url: str, proxies: dict = None, timeout: int = 30) -> bytes:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try:
        response = requests.get(url, proxies=proxies, timeout=timeout, verify=False)
        response.raise_for_status()
    except Exception as _err:
        error_as_string = ''.join(
            traceback.TracebackException.from_exception(_err).format()
        )
        logging.error(error_as_string)
    else:
        return response.content


def get_content_with_proxies_pool(url: str, proxies_pool: list) -> bytes:
    for proxies in proxies_pool:
        content = get_content(url, proxies=proxies)
        if not content:
            continue

        return content


def save_content_to_fs(content: bytes, file_path: str, override: bool = True):
    if os.path.exists(file_path) and not override:
        raise FileExistsError(f'File: {file_path} already exists')

    with open(file_path, 'wb') as file:
        file.write(content)


def create_proxy_dict(proxy: str) -> dict:
    return {i: f'{i}://{proxy}' for i in ('http', 'https')}


def check_proxy(proxy_list: list) -> list:
    valid_proxies = []
    for item in proxy_list:
        proxies = create_proxy_dict(item)
        content = get_content('https://api.ipify.org?format=json', proxies=proxies)
        if not content:
            continue
        valid_proxies.append(item)

    return valid_proxies


if __name__ == '__main__':
    proxies_pool = [create_proxy_dict(i) for i in ('84.17.51.209:3128', '84.17.51.212:3128', '84.17.51.213:3128')]
    for book_id in range(10):
        content = get_content_with_proxies_pool(f'https://tululu.org/txt.php?id={book_id}', proxies_pool=proxies_pool)
        if not content:
            continue

        save_content_to_fs(content, f'books//id{book_id}.txt')

