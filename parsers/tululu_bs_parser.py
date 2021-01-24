from urllib.parse import ParseResult, urlparse, urljoin

from bs4 import BeautifulSoup

from parsers.bs_parser_abstract import BsParserAbstract


class TululuBsParser(BsParserAbstract):

    def __init__(self):
        self.parsed_post_information: dict = dict()

    def parse_title_and_author(self, soup: BeautifulSoup) -> tuple:
        title: str = ''
        author: str = ''

        try:
            title = soup.find('div', id='content').find('h1').text.strip()
            title_splited: list = [i.strip() for i in title.split('::')]
            title, author = title_splited
        except Exception as _err:
            pass

        return title, author

    def parse_image_url(self, soup: BeautifulSoup):
        try:
            image_url = soup.find('div', class_='bookimage').find('a').find('img')['src']
        except Exception as _err:
            pass
        else:
            return image_url

    def parse_text(self, soup: BeautifulSoup):
        try:
            text = soup.findAll('table', class_='d_book')[1].find('tr').find('td').text
        except Exception as _err:
            pass
        else:
            return text.strip()

    def parse_url(self, soup):
        try:
            url = soup.select_one('a:-soup-contains("скачать txt")').get('href')
        except Exception as _err:
            pass
        else:
            return url

    def parse_comments(self, soup):
        try:
            comments = [i.contents[-1].text for i in soup.find_all('div', class_="texts")]
        except Exception as _err:
            pass
        else:
            return comments

    def parse_genres(self, soup):
        try:
            genres = [i.text for i in soup.find_all('a', title=lambda x: x and 'перейти к книгам этого жанра' in x)]
        except Exception as _err:
            pass
        else:
            return genres

    def parse(self, content: str, url: str):
        parsed_url: ParseResult = urlparse(url)
        site_url: str = '{}://{}'.format(parsed_url.scheme, parsed_url.netloc)

        soup: BeautifulSoup = BeautifulSoup(content, 'lxml')
        title, author = self.parse_title_and_author(soup)

        information_dict: dict = {
            'title': title,
            'author': author,
            'image_url': urljoin(site_url, self.parse_image_url(soup)),
            'text': self.parse_text(soup),
            'comments': self.parse_comments(soup) or [],
            'genres': self.parse_genres(soup),
            'url': urljoin(site_url, self.parse_url(soup))
        }

        return information_dict
