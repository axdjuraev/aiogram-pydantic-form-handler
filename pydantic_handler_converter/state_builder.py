from types import UnionType
from typing import Union, Type, get_origin, get_args
from aiogram.fsm.state import State, StatesGroup
from axabc.logging import SimpleFileLogger
from pydantic import BaseModel


def _is_union(obj):
    return get_origin(obj) in {Union, UnionType}


class SchemaStates(StatesGroup):
    def __init__(self, base_name: str) -> None:
        self._base_name = base_name

    @classmethod
    def create(cls, schema: Type[BaseModel], self = None) -> 'SchemaStates':
        self = self or cls(schema.__name__)

        for field in schema.__fields__.values():
            if not _is_union(field.type_) and not issubclass(field.type_, BaseModel):
                setattr(self, field.name, State(field.name, self._base_name))
                continue

            schemas = get_args(field.type_) if _is_union(field.type_) else (field.type_,)
            setattr(self, field.name, cls(f"{self._base_name}.{field.name}"))

            for schema in schemas:
                cls.create(schema, getattr(self, field.name))

        return self

