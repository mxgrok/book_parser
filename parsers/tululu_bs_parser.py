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
            return text

    def parse(self, content: str):
        soup: BeautifulSoup = BeautifulSoup(content, 'lxml')
        title, author = self.parse_title_and_author(soup)

        information_dict: dict = {
            'title': title,
            'author': author,
            'image_url': self.parse_image_url(soup),
            'text': self.parse_text(soup).strip(),
        }

        return information_dict
