from typing import Generic, Optional, TypeVar
from aiogram import Router
from aiogram.fsm.context import FSMContext
from pydantic import BaseModel

from pydantic_handler_converter.dialecsts import BaseDialects
from pydantic_handler_converter.types import Event, CallableWithNext

from .view import BaseView, ViewFactory
from .field_factory import logger
from .abstract_handler import AbstractPydanticFormHandlers
from .state_builder import SchemaStates


TBaseSchema = TypeVar("TBaseSchema", bound=BaseModel)


class BasePydanticFormHandlers(AbstractPydanticFormHandlers[TBaseSchema], Generic[TBaseSchema]):
    __abstract__ = True

    DIALECTS: BaseDialects = BaseDialects()
    start_point: BaseView
    views: dict[str, CallableWithNext[BaseView]]

    def __init__(self, router: Optional[Router] = None) -> None:
        self.router = router or Router()
        map(
            lambda view_elem: view_elem.elem.register2router(self.router), 
            self.views.values()
        )

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.views = {}
        cls.states = SchemaStates.create(cls.Schema)
        view_factory = ViewFactory()

        views = view_factory.create_by_schema(
            cls.Schema, 
            states=cls.states, 
            dialects=cls.DIALECTS,
            parents=(cls.Schema.__name__,)
        )
        views_count = len(views)

        for num, view in enumerate(views, start=1):
            view_name = view.name
            try:
                getattr(cls, view_name)
                logger.info(f"[{cls.__name__}][__init_subclass__][view][skip]: {view_name=}")
            except AttributeError:
                setattr(cls, view_name, view.__call__)
                next = views[num] if num < views_count else None
                cls.views[view.step_name] = CallableWithNext(view, next=next)

        if not cls.views:
            raise ValueError(f'Could not create views for schema `{cls.Schema}`')

        cls.start_point = tuple(cls.views.values())[0].elem

    async def next(self, event: Event, state: FSMContext, current_step: Optional[str] = None):
        try:
            if not current_step:
                return await self.start_point(self, event, state)

            return await self.views[current_step].next(self, event, state)
        except NotImplementedError:
            return await self.finish(event, state)

    async def finish(self, event: Event, state: FSMContext):
        return await super().finish(event, state)

    def register2router(self, router: Router) -> Router:
        return router.include_router(self.router)

