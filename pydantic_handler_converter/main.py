from typing import Generic, TypeVar
from aiogram import Router
from pydantic import BaseModel

from .view import ViewFactory
from .abstract_handler import AbstractPydanticFormHandlers


TBaseSchema = TypeVar("TBaseSchema", bound=BaseModel)


class BasePydanticFormHandlers(AbstractPydanticFormHandlers[TBaseSchema], Generic[TBaseSchema]):
    __abstract__ = True

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.views = []
        view_factory = ViewFactory()

        for field in cls.Schema.__fields__.values():
            for view in view_factory.create(field):
                setattr(cls, view.name, view.__call__)
                cls.views.append(view)

    def register2router(self, router: Router) -> Router:
        for view in self.views:
            view.register2router(router)

        return router

