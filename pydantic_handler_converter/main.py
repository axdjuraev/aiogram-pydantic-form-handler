from typing import Generic, TypeVar
from pydantic import BaseModel

from .view import ViewFactory
from .abstract_handler import AbstractPydanticFormHandlers


TBaseSchema = TypeVar("TBaseSchema", bound=BaseModel)


class BasePydanticFormHandlers(AbstractPydanticFormHandlers[TBaseSchema], Generic[TBaseSchema]):
    __abstract__ = True

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        ViewFactory.create(cls.Schema)

