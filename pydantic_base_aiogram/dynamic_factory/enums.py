from enum import Enum

from pydantic_base_aiogram.types import FileType, Album, OptionalFile, OptionalAlbum


class DescriptiveEnum(Enum):
    def __init__(self, name, description) -> None:
        self._name = name
        self._description = description
                                                   
    @property
    def short_name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description


class InputFormTypesEnum(DescriptiveEnum):
    Integer = (int.__name__, 'Целочисленный тип')
    Float = (float.__name__, 'Число с плавающей точкой')
    String = (str.__name__, 'Строка')
    File = (FileType.__name__, 'Файл')
    FileOptional = (OptionalFile.__name__, 'Файл по выбору')
    Album = (Album.__name__, 'Альбом')
    AlbumOptional = (OptionalAlbum.__name__, 'Альбом по выбору')
