from typing import Type
from inspect import isclass
from aiogram.fsm.state import State, StatesGroup
from pydantic import BaseModel


class SchemaStates(StatesGroup):
    def __init__(self, base_name: str) -> None:
        self._base_name = base_name

    @classmethod
    def create(cls, schema: Type[BaseModel], self = None) -> 'SchemaStates':
        self = self or cls(schema.__name__)

        for field in schema.__fields__.values():
            if not isclass(field.type_) or not issubclass(field.type_, BaseModel):
                setattr(self, field.name, State(field.name, self._base_name))
                continue
                
            setattr(self, field.name, cls(f"{self._base_name}.{field.name}"))
            cls.create(field.type_, getattr(self, field.name))

        return self

