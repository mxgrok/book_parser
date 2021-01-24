from abc import ABC, abstractmethod


class BsParserAbstract(ABC):

    @abstractmethod
    def parse(self, content: str, url: str):
        pass
