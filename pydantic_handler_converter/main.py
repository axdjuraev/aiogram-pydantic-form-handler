from typing import Generic, Iterable, TypeVar
from aiogram import Router
from pydantic import BaseModel

from pydantic_handler_converter.dialecsts import BaseDialects

from .view import BaseView, ViewFactory
from .field_factory import logger
from .abstract_handler import AbstractPydanticFormHandlers
from .state_builder import SchemaStates


TBaseSchema = TypeVar("TBaseSchema", bound=BaseModel)


class BasePydanticFormHandlers(AbstractPydanticFormHandlers[TBaseSchema], Generic[TBaseSchema]):
    __abstract__ = True

    DIALECTS: BaseDialects = BaseDialects()
    views: list[BaseView]

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.views = []
        cls.states = SchemaStates.create(cls.Schema)
        view_factory = ViewFactory()

        for field in cls.Schema.__fields__.values():
            back_data = cls.views[-1].callback_data if cls.views else None
            views = view_factory.create(
                field, 
                states=cls.states, 
                back_data=back_data,
                dialects=cls.DIALECTS,
                parents=(cls.Schema.__name__,)
            )
            views = views if isinstance(views, Iterable) else (views,)
            logger.info(f"[{cls.__name__}][__init_subclass__]: {views=}")
            for view in views:
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

