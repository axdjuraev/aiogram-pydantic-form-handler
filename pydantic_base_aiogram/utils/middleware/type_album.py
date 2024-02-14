from typing import TYPE_CHECKING, Iterable


if TYPE_CHECKING:
    from pydantic_base_aiogram.types import FileType


class Album:
    def __init__(self) -> None:
        self._items: 'list[FileType]' = []
        self.max_bytes = 0
        self.html_contents = []

    def add(self, obj: 'FileType'):
        self._items.append(obj)
        self.max_bytes += obj.file.file_size or 0
        self.html_contents.append(obj.msg.html_text)

    def extend(self, other: 'Album'):
        self._items.extend(other._items)
        self.max_bytes += other.max_bytes
        self.html_contents.extend(other.html_contents)

    def __iter__(self) -> 'Iterable[FileType]':
        return iter(self._items)
    
    def __getitem__(self, index):
        return self._items[index]
