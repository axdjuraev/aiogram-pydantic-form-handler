from abc import ABC
from typing import Type, TypeVar, Generic
from aiogram.fsm.state import StatesGroup
from pydantic import BaseModel

from .abstract_view import AbstractView


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

