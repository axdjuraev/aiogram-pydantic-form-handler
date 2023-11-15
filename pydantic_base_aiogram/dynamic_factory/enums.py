from enum import Enum


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
  Integer = ('int', 'Целочисленный тип')
  Float = ('float', 'Число с плавающей точкой')
  String = ('str', 'Строка')

