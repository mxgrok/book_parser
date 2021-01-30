from urllib.parse import urljoin
from contextlib import suppress

from bs4 import BeautifulSoup

from parsers.bs_parser_abstract import BsParserAbstract


class TululuBsParser(BsParserAbstract):

    def __init__(self):
        self.parsed_post_information: dict = dict()

    def parse_title_and_author(self, soup: BeautifulSoup) -> tuple:
        with suppress(Exception):
            title = soup.find('div', id='content').find('h1').text.strip()
            title_splited: list = [item.strip() for item in title.split('::')]
            title, author = title_splited

        return title, author

    def parse_image_url(self, soup: BeautifulSoup):
        with suppress(Exception):
            image_url = soup.find('div', class_='bookimage').find('a').find('img')['src']

            return image_url

    def parse_text(self, soup: BeautifulSoup):
        with suppress(Exception):
            text = soup.findAll('table', class_='d_book')[1].find('tr').find('td').text

            return text.strip()

    def parse_url(self, soup):
        with suppress(Exception):
            url = soup.select_one('a:-soup-contains("скачать txt")').get('href')

            return url

    def parse_comments(self, soup):
        with suppress(Exception):
            comments = [item.contents[-1].text for item in soup.find_all('div', class_="texts")]
            return comments

    def parse_genres(self, soup):
        with suppress(Exception):
            genres = [
                item.text for item in soup.find_all('a', title=lambda x: x and 'перейти к книгам этого жанра' in x)
            ]

            return genres

    def parse(self, content: str, url: str):
        soup: BeautifulSoup = BeautifulSoup(content, 'lxml')
        title, author = self.parse_title_and_author(soup)

        information_dict: dict = {
            'title': title,
            'author': author,
            'image_url': urljoin(url, self.parse_image_url(soup)),
            'text': self.parse_text(soup),
            'comments': self.parse_comments(soup) or [],
            'genres': self.parse_genres(soup),
            'url': urljoin(url, self.parse_url(soup))
        }

        return information_dict
