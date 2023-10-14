from typing import Awaitable, Callable, Generic, Iterable, Optional, TypeVar
from aiogram import Router
from aiogram.fsm.context import FSMContext
from pydantic import BaseModel

from pydantic_handler_converter.dialecsts import BaseDialects
from pydantic_handler_converter.types import Event, CallableWithNext, BaseSingleHandler

from .view import BaseView, ViewFactory
from .controller import ControllerFactory
from .field_factory import logger
from .abstract_handler import AbstractPydanticFormHandlers
from .state_builder import SchemaStates


TBaseSchema = TypeVar("TBaseSchema", bound=BaseModel)


class BasePydanticFormHandlers(AbstractPydanticFormHandlers[TBaseSchema], Generic[TBaseSchema]):
    __abstract__ = True

    DIALECTS: BaseDialects = BaseDialects()
    start_point: BaseView
    views: dict[str, CallableWithNext[BaseView]]
    controllers: dict[str, CallableWithNext[BaseView]]

    def __init__(self, finish_call: Callable[[TBaseSchema, Event, FSMContext], Awaitable], router: Optional[Router] = None) -> None:
        self._finish_call = finish_call
        self.router = router or Router()
        self._register_bindabls(tuple(self.views.values()))  # type: ignore
        self._register_bindabls(tuple(self.controllers.values()))  # type: ignore

    def _register_bindabls(self, elems: Iterable[CallableWithNext[BaseSingleHandler]]) -> None:
        for item in elems:
            if not item.elem.is_custom:
                item.elem.bind(self)

            item.elem.register2router(self.router)

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.states = SchemaStates.create(cls.Schema)
        data = {
            'schema': cls.Schema,
            'states': cls.states,
            'dialects': cls.DIALECTS,
            'parents': (cls.Schema.__name__,)
        }

        cls.views = cls._register_nextabls(ViewFactory().create_by_schema(**data))
        cls.controllers = cls._register_nextabls(ControllerFactory().create_by_schema(**data))

        if not cls.views:
            raise ValueError(f'Could not create views for schema `{cls.Schema}`')

        cls.start_point = tuple(cls.views.values())[0].elem

    @classmethod
    def _register_nextabls(cls, nextabls: list[BaseSingleHandler]) -> dict[str, CallableWithNext]:
        res = {}
        all_count = len(nextabls)

        for num, elem in enumerate(nextabls, start=1):
            elem_name = elem.name
            next = nextabls[num] if num < all_count else None

            try:
                if next:
                    next = getattr(cls, next.name)
            except AttributeError:
                pass

            try:
                elem.__call__ = getattr(cls, elem_name)
                elem.is_custom = True
                logger.info(f"[{cls.__name__}][_register_nextabls][skip]: {elem_name=}")
            except AttributeError:
                setattr(cls, elem_name, elem.__call__)

            res[elem.step_name] = CallableWithNext(elem, next=next)

        return res

    async def next(self, event: Event, state: FSMContext, current_step: Optional[str] = None):
        try:
            if not current_step:
                return await self.start_point(self, event, state)

            return await self.views[current_step].next(self, event, state)
        except NotImplementedError:
            return await self.finish(event, state)

    async def finish(self, event: Event, state: FSMContext):
        data = await state.get_data()
        logger.debug(f"[{self.__class__.__name__}][finish]: {locals()=}")

        schema = self.Schema(**data[self.Schema.__name__])
        return await self._finish_call(schema, event, state)

    def register2router(self, router: Router) -> Router:
        return router.include_router(self.router)

