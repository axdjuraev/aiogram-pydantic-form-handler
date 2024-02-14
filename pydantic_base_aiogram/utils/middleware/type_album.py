from typing import Iterable
from pydantic_base_aiogram.types import FileType


class Album:
    def __init__(self) -> None:
        self._items: list[FileType] = []
        self.max_bytes = 0
        self.html_contents = []

    def add(self, obj: FileType):
        self._items.append(obj)
        self.max_bytes += obj.file.file_size or 0
        self.html_contents.append(obj.msg.html_text)

    def __iter__(self) -> Iterable[FileType]:
        return iter(self._items)
    
    def __getitem__(self, index):
        return self._items[index]
