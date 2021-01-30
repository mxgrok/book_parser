import os
import uuid

from pathvalidate import sanitize_filename, sanitize_filepath

from storages.storage_abstract import StorageAbstract


class FileSystemStorage(StorageAbstract):

    def __init__(self, file_system_path: str):
        self.file_system_path: str = file_system_path
        self.is_file_system_path_exists: bool = False

    def create_file_system_path(self):
        os.makedirs(self.file_system_path, exist_ok=True)
        self.is_file_system_path_exists = True

    def save(self, content: bytes, name: str):
        if not self.is_file_system_path_exists:
            self.create_file_system_path()

        unique: str = str(uuid.uuid4())
        name = f'{unique}-name'

        file_path: str = os.path.join(
            self.file_system_path,
            sanitize_filename(name)
        )
        with open(file_path, 'wb') as file:
            file.write(content)
