from types import MethodType
from typing import Awaitable, Callable, Generic, Iterable, Optional, TypeAlias, TypeVar, Union
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from pydantic import BaseModel

from pydantic_base_aiogram.dialecsts import BaseDialects
from pydantic_base_aiogram.types import Event, CallableWithNext, BaseSingleHandler
from pydantic_base_aiogram.utils.middleware.type_album import Album
from pydantic_base_aiogram.utils.reference_register import ReferenceRegister

from .view import ViewFactory
from .controller import ControllerFactory
from .field_factory import logger
from .abstract_handler import AbstractPydanticFormHandlers
from .state_builder import SchemaStates
from .utils.add_more_handlers import AddMoreHandlers


TBaseSchema = TypeVar("TBaseSchema", bound=BaseModel)
TBackData: TypeAlias = Optional[Union[str, ReferenceRegister, 'ellipsis']]


class SchemaBaseHandlersGroup(AbstractPydanticFormHandlers[TBaseSchema], Generic[TBaseSchema]):
    __abstract__ = True
    __full_laad__ = True

    _DEFAULT_ALBUM_MIDDLEWARE_LATENCY = 0.01
    DIALECTS: BaseDialects = BaseDialects()
    BACK_ALLOWED = True
    STATE_BASE_MANAGE: bool = False
    FORCE_DYNAMIC_KEYBOARD = False

    base_cq_prefix: str
    back_data: TBackData = None
    views: dict[str, CallableWithNext]
    controllers: dict[str, CallableWithNext]
    step_tree_tails: dict[str, list[CallableWithNext]] = {}
    _except_steps: list = []
    _add_more_handlers = None
    _reference_register: ReferenceRegister

    def __init__(
        self, 
        finish_call: Callable[[TBaseSchema, Event, FSMContext], Awaitable], 
        router: Optional[Router] = None,
        album_middleware_latency: Optional[float] = None,
        *,
        back_data_getter: Optional[Callable] = None, 
    ) -> None:
        self._finish_call = finish_call
        self.router = router or Router()
        self._register_bindabls(tuple(self.controllers.values()))  # type: ignore
        self._register_bindabls(tuple(self.views.values()))  # type: ignore
        self._add_more_handlers = AddMoreHandlers(
            self.add_more_final_call, 
            self.DIALECTS, 
            self.base_cq_prefix,
            self.DIALECTS.BACK_BUTTON_DATA,
        )
        self._album_middleware_latency = (
            album_middleware_latency 
            or self._DEFAULT_ALBUM_MIDDLEWARE_LATENCY
        )
        self._back_data_getter = back_data_getter or self._back_data_getter
        self.__class__._reference_register.bind(self._back_data_getter)

    def _back_data_getter(self):
        return None

    async def add_more_final_call(self, event, state, choice: int):
        step_name = await self._get_current_step(state)

        if choice:
            return await self.next(event, state, step_name, restart_loop=True)
        
        return await self.next(event, state, step_name, skip_loop_prompt=True)

    def _register_bindabls(self, elems: Iterable[CallableWithNext]) -> None:
        for item in elems:
            if not item.elem.is_custom:
                item.elem.bind(self)

            item.elem.register2router(self.router)

    def __init_subclass__(cls, back_data: TBackData = None) -> None:
        if not super().__init_subclass__():
            return

        cls._reference_register = ReferenceRegister()
        cls.states = SchemaStates.create(cls.Schema)
        cls.base_cq_prefix = cls.Schema.__name__.lower()

        cls.back_data = back_data or cls.back_data

        if cls.back_data is ...:
            cls.back_data = cls._reference_register

        data = {
            'schema': cls.Schema,
            'states': cls.states,
            'dialects': cls.DIALECTS,
            'parents': (cls.Schema.__name__,),
            '_except_steps': cls._except_steps,
            'back_allowed': cls.BACK_ALLOWED,
            'base_cq_prefix': cls.base_cq_prefix,
            'back_data': cls.back_data,
            'state_base_manage': cls.STATE_BASE_MANAGE,
            'force_dynamic_keyboard': cls.FORCE_DYNAMIC_KEYBOARD,
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
        last_index = len(nextabls) - 1

        for index, elem in enumerate(nextabls):
            logger.info(f"[{cls.__name__}][_register_nextabls][step_process]: {elem=}")
            elem_name = elem.name

            try:
                val = getattr(cls, elem_name)

                if isinstance(val, MethodType) and isinstance(val.__self__, BaseSingleHandler) and elem.tree_id:
                    pix = elem.tree_id - 1

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

            if current.elem.tree_id is None or last_index == index:
                if last_index == index:
                    previous_elem = current
                    current = None

                if previous_elem and previous_elem.elem.tree_id is not None:
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
            elif current.elem.tree_id != previous_tree_id and previous_elem is not None:
                if previous_tree_id is not None:
                    tree_tails.append(previous_elem)

                tree_sub_heads.append(current)

            previous_elem = current

            if current:
                previous_tree_id = current.elem.tree_id

        return res

    async def show_add_more_view(self, event: Event, _: FSMContext):
        return await self._add_more_handlers.view(event._event)

    async def next(
        self, 
        event: Event, 
        state: FSMContext, 
        current_step: Optional[str] = None,
        *,
        skip_loop_prompt: bool = False,
        restart_loop: bool = False,
        **kwargs,
    ):
        try:
            update = event

            if isinstance(event, Event):
                update = event._event
            else:
                event = Event(event)
            
            if not current_step:
                return await self.start_point(self, update, state, **kwargs)

            current = self.views[current_step]

            if (
                current.elem.tree_id
                and (_s := current.elem.tree_head_step_name)
                and (choice_index := await self._get_tree_index_choice(state, _s))
                and (new_branch := self.views.get(f"{current_step}{choice_index}"))
            ):  # possibity of alternative branches
                current = new_branch
            
            if (
                not skip_loop_prompt
                and current.elem.is_list_item
                and (parent_name := current.elem.tree_head_step_name)
                and (parent_view := self.views.get(parent_name))
                and (
                    not current._next 
                    or current._next.elem.parents != current.elem.parents
                )
            ):
                if restart_loop:
                    return await parent_view.elem.__call__(update, state, **kwargs) 

                return await self.show_add_more_view(event, state)

            return await current.next(update, state, **kwargs)

        except NotImplementedError:
            return await self.finish(event, state)

    async def back(self, event: CallbackQuery, state: FSMContext, *, current_step=None):
        current_step = current_step or await self._get_current_step(state)

        try:
            if not current_step:
                raise NotImplementedError

            current = self.views[current_step]

            if (
                current._previos
                and current._previos.elem.tree_id
                and current._previos.elem.tree_id != current.elem.tree_id
                and (_s := current._previos.elem.tree_head_step_name)
                and (tails := self.step_tree_tails.get(_s))
                and (choice_index := await self._get_tree_index_choice(state, _s)) is not None
            ):
                await tails[choice_index].elem(self, event, state)
            else:
                await current.back(event, state)

        except NotImplementedError:
            return await self.start_point(self, event, state)

    async def skip(self, event: CallbackQuery, state: FSMContext):
        current_step = await self._get_current_step(state)
        return await self.next(Event(event), state, current_step)  # type: ignore

    async def finish(self, event: Event, state: FSMContext):
        data = await state.get_data()
        logger.debug(f"[{self.__class__.__name__}][finish]: {locals()=}")

        try:
            schema = await self.convert_final_data(data)
        except Exception as e:
            return print(f"{e=}")

        return await self._finish_call(schema, event, state)

    async def convert_final_data(self, data: dict):
        return self.Schema(**data[self.Schema.__name__])
    
    @staticmethod
    async def _get_files(state: FSMContext, state_data: "dict | None" = None):
        if not state_data:
            state_data = await state.get_data()

        return state_data.get('__files__', {})

    @classmethod
    async def _get_all_state_files(cls, state: FSMContext):
        res = Album()
        all_files = await cls._get_files(state)

        for v in (all_files).values():
            res.extend(v)

        return res

    @staticmethod
    async def _get_state_files(key, state: FSMContext):
        state_data = await state.get_data()
        state_files = state_data.get('__files__', {})
        return state_files.get(key, Album())

    @classmethod
    async def _add_state_files(cls, key, data: Album, state: FSMContext):
        state_files = await cls._get_files(state)

        album: Album = state_files.get(key, Album())
        album.extend(data)

        state_files[key] = album
        await state.update_data(__files__=state_files)

    @classmethod
    async def _remove_state_files(cls, key, state: FSMContext):
        state_files = await cls._get_files(state)
        
        if key in state_files:
            del state_files[key]
            await state.update_data(__files__=state_files)

    async def _get_current_step(self, state: FSMContext):
        return (await state.get_data()).get('__step__')

    async def _get_tree_index_choice(self, state: FSMContext, step_name: str):
        return (await state.get_data()).get(f'__tree_choice_{step_name}__')

    def register2router(self, router: Router) -> Router:
        router.callback_query(F.data == f"{self.base_cq_prefix}_{self.DIALECTS.BACK_BUTTON_DATA}")(self.back)
        router.callback_query(F.data == f"{self.base_cq_prefix}_{self.DIALECTS.SKIP_STEP_DATA}")(self.skip)

        router.include_router(self.router)

        if self._add_more_handlers:
            self._add_more_handlers.register2router(router)

        logger.debug(f"[{self.__class__.__name__}]: router registered")

        return router
 
