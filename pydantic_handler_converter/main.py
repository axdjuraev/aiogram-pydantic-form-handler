from typing import Generic, TypeVar
from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from pydantic import BaseModel

from .view import ViewFactory, logger
from .abstract_handler import AbstractPydanticFormHandlers


TBaseSchema = TypeVar("TBaseSchema", bound=BaseModel)


class BasePydanticFormHandlers(AbstractPydanticFormHandlers[TBaseSchema], Generic[TBaseSchema]):
    __abstract__ = True

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.views = []
        cls.states = StatesGroup()
        view_factory = ViewFactory()

        for field in cls.Schema.__fields__.values():
            setattr(cls.states, field.name, State(field.name))
            for view in view_factory.create(field):
                view_name = view.name
                try:
                    getattr(cls, view_name)
                    logger.info(f"[{cls.__name__}][__init_subclass__][skip]: {field.name=}")
                except AttributeError:
                    setattr(cls, view_name, view.__call__)
                    cls.views.append(view)

    def register2router(self, router: Router) -> Router:
        for view in self.views:
            view.register2router(router)

        return router

