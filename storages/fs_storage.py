import os

from storages.storage_abstract import StorageAbstract


class FileSystemStorage(StorageAbstract):

    def __init__(self, file_system_path: str):
        self.file_system_path: str = self.create_file_system_path(file_system_path)

    @staticmethod
    def create_file_system_path(file_system_path: str) -> str:
        os.makedirs(file_system_path, exist_ok=True)

        return file_system_path

    def save(self, content: bytes, name: str):
        file_path: str = os.path.join(self.file_system_path, name)
        with open(file_path, 'wb') as file:
            file.write(content)
