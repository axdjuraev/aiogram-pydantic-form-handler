from abc import ABC, abstractmethod
from typing import Type, TypeVar, Generic
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup
from pydantic import BaseModel

from pydantic_handler_converter.types import Event

from .view.abstract import AbstractView


TBaseSchema = TypeVar("TBaseSchema", bound=BaseModel)


class AbstractPydanticFormHandlers(ABC, Generic[TBaseSchema]):
    Schema: Type[TBaseSchema]
    views: list[AbstractView]
    states: StatesGroup

    __abstract__ = True
    def __init_subclass__(cls) -> None:
        if cls.__abstract__ and '__abstract__' in cls.__dict__:
            return

        e = NotImplementedError(f"`{cls.__name__}` requires Pydantic.BaseModel")
 
        if (
            not (bases := getattr(cls, "__orig_bases__"))
            or not (generics := bases[0].__args__)
        ):
            raise e

        cls.Schema = generics[-1]

        if not issubclass(cls.Schema, BaseModel):
            raise e

    @abstractmethod
    async def next(self, current_step: str, event: Event, state: FSMContext):
        raise NotImplementedError

    @abstractmethod
    async def finish(self, event: Event, state: FSMContext):
        raise NotImplementedError

