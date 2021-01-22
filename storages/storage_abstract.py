from abc import ABC, abstractmethod


class StorageAbstract(ABC):

    @abstractmethod
    def save(self, content: bytes, name: str):
        pass
