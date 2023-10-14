from types import MethodType
from typing import Awaitable, Callable, Generic, Iterable, Optional, TypeVar
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
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
        previous_elem: Optional[CallableWithNext] = None
        previous_tree_id: Optional[int] = None
        tree_tails: list[CallableWithNext] = []

        for elem in nextabls:
            elem_name = elem.name

            try:
                val = getattr(cls, elem_name)

                if isinstance(val, MethodType) and isinstance(val.__self__, BaseSingleHandler):
                    logger.info(f"[{cls.__name__}][_register_nextabls][dublicate]: {elem_name=}")
                    continue

                elem.__call__ = val
                elem.is_custom = True
                logger.info(f"[{cls.__name__}][_register_nextabls][skip]: {elem_name=}")
            except AttributeError:
                setattr(cls, elem_name, elem.__call__)

            current = CallableWithNext(elem, previos=previous_elem)
            res[elem.step_name] = current

            if previous_elem is not None:
                previous_elem.set_next(current)

            if current.elem.tree_id is None:
                if previous_elem is not None:
                    tree_tails.append(previous_elem)

                    while tree_tails and (tail := tree_tails.pop()):
                        tail.set_next(current)
            elif current.elem.tree_id != previous_tree_id and previous_elem is not None:
                tree_tails.append(previous_elem)

            previous_elem = current
            previous_tree_id = current.elem.tree_id

        return res

    async def _get_current_step(self, state: FSMContext):
        return (await state.get_data()).get('__step__')

    async def next(self, event: Event, state: FSMContext, current_step: Optional[str] = None):
        try:
            if not current_step:
                return await self.start_point(self, event, state)

            return await self.views[current_step].next(event, state)
        except NotImplementedError:
            return await self.finish(event, state)

    async def back(self, event: CallbackQuery, state: FSMContext):
        current_step = await self._get_current_step(state)
        try:
            if not current_step:
                raise NotImplementedError
            return await self.views[current_step].back(event, state)
        except NotImplementedError:
            return await self.start_point(self, event, state)

    async def finish(self, event: Event, state: FSMContext):
        data = await state.get_data()
        logger.debug(f"[{self.__class__.__name__}][finish]: {locals()=}")

        schema = self.Schema(**data[self.Schema.__name__])
        return await self._finish_call(schema, event, state)

    def register2router(self, router: Router) -> Router:
        router.callback_query(F.data == self.DIALECTS.BACK_BUTTON_DATA)(self.back)
        return router.include_router(self.router)

