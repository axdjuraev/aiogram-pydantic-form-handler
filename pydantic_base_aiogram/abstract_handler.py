from abc import ABC, abstractmethod
from typing import Optional, Type, TypeVar, Generic, Union
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup
from pydantic import BaseModel

from pydantic_base_aiogram.types import Event

from .view.abstract import AbstractView


TBaseSchema = TypeVar("TBaseSchema", bound=BaseModel)


class AbstractPydanticFormHandlers(ABC, Generic[TBaseSchema]):
    Schema: Type[TBaseSchema]
    views: list[AbstractView]
    states: StatesGroup

    __abstract__ = True
    def __init_subclass__(cls) -> Union[bool, None]:
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

        return True

    @abstractmethod
    async def next(self, event: Event, state: FSMContext, current_step: Optional[str] = None):
        raise NotImplementedError

    @abstractmethod
    async def finish(self, event: Event, state: FSMContext):
        raise NotImplementedError

