from inspect import isclass
from typing import Optional, Type
from pydantic import BaseModel
from aiogram.fsm.state import State, StatesGroup

from pydantic_base_aiogram.utils.field_normalization import TypeNormilizer


class SchemaStates(StatesGroup):
    _type_normilizer = TypeNormilizer()

    def __init__(self, base_name: str) -> None:
        self._base_name = base_name

    @classmethod
    def create(cls, schema: Type[BaseModel], self: Optional['SchemaStates'] = None) -> 'SchemaStates':
        self = self or cls(schema.__name__)

        for field in schema.__fields__.values():
            types, _ = self._type_normilizer.normalize_type(field.type_)
            child: Optional['SchemaStates'] = None

            for t in types:
                if isclass(t) and issubclass(t, BaseModel):
                    if not child:
                        child = cls(f"{self._base_name}.{field.name}")
                        setattr(self, field.name, child)

                    cls.create(t, child)
                else:
                    setattr(self, field.name, State(field.name, self._base_name))

        return self

