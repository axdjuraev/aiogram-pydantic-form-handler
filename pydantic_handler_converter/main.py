from contextlib import contextmanager
from types import MethodType
from typing import Awaitable, Callable, Generic, Iterable, Optional, TypeVar
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from pydantic import BaseModel

from pydantic_handler_converter.dialecsts import BaseDialects
from pydantic_handler_converter.types import Event, CallableWithNext, BaseSingleHandler

from .view import ViewFactory
from .controller import ControllerFactory
from .field_factory import logger
from .abstract_handler import AbstractPydanticFormHandlers
from .state_builder import SchemaStates


TBaseSchema = TypeVar("TBaseSchema", bound=BaseModel)


class BasePydanticFormHandlers(AbstractPydanticFormHandlers[TBaseSchema], Generic[TBaseSchema]):
    __abstract__ = True

    DIALECTS: BaseDialects = BaseDialects()
    BACK_ALLOWED = True

    views: dict[str, CallableWithNext]
    controllers: dict[str, CallableWithNext]
    step_tree_tails: dict[str, list[CallableWithNext]] = {}
    _except_steps: list = []

    def __init__(self, finish_call: Callable[[TBaseSchema, Event, FSMContext], Awaitable], router: Optional[Router] = None) -> None:
        self._finish_call = finish_call
        self.router = router or Router()
        self._register_bindabls(tuple(self.views.values()))  # type: ignore
        self._register_bindabls(tuple(self.controllers.values()))  # type: ignore

    def _register_bindabls(self, elems: Iterable[CallableWithNext]) -> None:
        for item in elems:
            if not item.elem.is_custom:
                item.elem.bind(self)

            item.elem.register2router(self.router)

    def __init_subclass__(cls) -> None:
        if not super().__init_subclass__():
            return 

        cls.states = SchemaStates.create(cls.Schema)
        data = {
            'schema': cls.Schema,
            'states': cls.states,
            'dialects': cls.DIALECTS,
            'parents': (cls.Schema.__name__,),
            '_except_steps': cls._except_steps,
            'back_allowed': cls.BACK_ALLOWED,
        }

        cls.views = cls._register_nextabls(ViewFactory().create_by_schema(**data), set_step_tree_tails=True)
        cls.controllers = cls._register_nextabls(ControllerFactory().create_by_schema(**data))

        if not cls.views:
            raise ValueError(f'Could not create views for schema `{cls.Schema}`')

        cls.start_point = tuple(cls.views.values())[0].elem  # type: ignore

    @classmethod
    def _register_nextabls(cls, nextabls: list[BaseSingleHandler], set_step_tree_tails = False) -> dict[str, CallableWithNext]:
        res = {}
        previous_elem: Optional[CallableWithNext] = None
        previous_tree_id: Optional[int] = None
        tree_head: Optional[CallableWithNext] = None
        tree_sub_heads: list[CallableWithNext] = []
        tree_tails: list[CallableWithNext] = []
        _last_dublicates_tree_indexes = {}

        for elem in nextabls:
            logger.info(f"[{cls.__name__}][_register_nextabls][step_process]: {elem=}")

            if elem is None or elem.step_name in cls._except_steps:
                continue

            elem_name = elem.name

            try:
                val = getattr(cls, elem_name)

                if isinstance(val, MethodType) and isinstance(val.__self__, BaseSingleHandler):
                    pix = _last_dublicates_tree_indexes.get(elem.step_name, 0) + 1
                    _last_dublicates_tree_indexes[elem.step_name] = pix

                    elem.name = f"{elem.name}{pix}"
                    elem.step_name = f"{elem.step_name}{pix}"

                    logger.info(f"[{cls.__name__}][_register_nextabls][dublicate]: {elem_name=}")
                else:
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
                if previous_elem and previous_elem.elem.tree_id:
                    tree_tails.append(previous_elem)

                    if tree_head:
                        if set_step_tree_tails and tree_tails:
                            cls.step_tree_tails[tree_head.elem.step_name] = tree_tails.copy()

                        while tree_sub_heads and (head := tree_sub_heads.pop()):
                            head.set_previos(tree_head)

                        tree_head = None

                    while tree_tails and (tail := tree_tails.pop()):
                        tail.set_next(current)

                tree_head = current
            elif (
                current.elem.tree_id != previous_tree_id 
                and previous_tree_id is not None
                and previous_elem is not None
            ):
                tree_tails.append(previous_elem)

            previous_elem = current
            previous_tree_id = current.elem.tree_id

        if tree_head and previous_elem:
            tree_tails.append(previous_elem)

            for tail in tree_tails:
                tail._next = None

        return res

    async def next(self, event: Event, state: FSMContext, current_step: Optional[str] = None):
        try:
            if not current_step:
                return await self.start_point(self, event, state)

            current = self.views[current_step]
            
            if (
                not self.views.get(f"{current_step}1") 
                or not (_s := current.elem.tree_head_step_name)
                or not (choice_index := await self._get_tree_index_choice(state, _s))
            ):  # possibity of alternative branches
                return await current.next(event, state)

            return await self.views[f"{current_step}{choice_index}"].next(event, state)

        except NotImplementedError:
            return await self.finish(event, state)

    async def back(self, event: CallbackQuery, state: FSMContext):
        current_step = await self._get_current_step(state)
        try:
            if not current_step:
                raise NotImplementedError

            current = self.views[current_step]

            if (
                current._previos
                and current.elem.tree_id != current._previos.elem.tree_id
                and (_s := current._previos.elem.tree_head_step_name)
                and (tails := self.step_tree_tails.get(_s))
                and (choice_index := await self._get_tree_index_choice(state, _s)) is not None
            ):
                await tails[choice_index].elem(self, event, state)
            else:
                await current.back(event, state)

        except NotImplementedError:
            return await self.start_point(self, event, state)

    async def finish(self, event: Event, state: FSMContext):
        data = await state.get_data()
        logger.debug(f"[{self.__class__.__name__}][finish]: {locals()=}")

        schema = self.Schema(**data[self.Schema.__name__])
        return await self._finish_call(schema, event, state)

    async def _get_current_step(self, state: FSMContext):
        return (await state.get_data()).get('__step__')

    async def _get_tree_index_choice(self, state: FSMContext, step_name: str):
        return (await state.get_data()).get(f'__tree_choice_{step_name}__')

    def register2router(self, router: Router) -> Router:
        router.callback_query(F.data == self.DIALECTS.BACK_BUTTON_DATA)(self.back)
        return router.include_router(self.router)

