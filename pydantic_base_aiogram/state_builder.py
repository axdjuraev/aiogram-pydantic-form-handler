from enum import Enum
from inspect import isclass
from types import UnionType
from typing import Union, Type, get_origin, get_args
from aiogram.fsm.state import State, StatesGroup
from pydantic import BaseModel


def is_union(obj):
    return get_origin(obj) in {Union, UnionType}


class SchemaStates(StatesGroup):
    def __init__(self, base_name: str) -> None:
        self._base_name = base_name

    @classmethod
    def create(cls, schema: Type[BaseModel], self = None) -> 'SchemaStates':
        self = self or cls(schema.__name__)

        for field in schema.__fields__.values():
            type_ = field.type_

            if (
                (isclass(type_) and issubclass(type_, BaseModel)) 
                or (is_union(type_) and issubclass(get_args(type_)[-1], BaseModel))
            ):
                schemas = get_args(field.type_) if is_union(field.type_) else (field.type_,)
                setattr(self, field.name, cls(f"{self._base_name}.{field.name}"))

                for schema in schemas:
                    cls.create(schema, getattr(self, field.name))

                continue

            setattr(self, field.name, State(field.name, self._base_name))

        return self

