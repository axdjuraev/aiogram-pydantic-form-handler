from typing import Any, Callable, Iterable, Optional, Union
from aiogram.types import InlineKeyboardMarkup, Message
from pydantic.fields import ModelField
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State

from pydantic_base_aiogram.types import DataGetterCallable, Event
from pydantic_base_aiogram.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_base_aiogram.field_factory import logger
from pydantic_base_aiogram.utils.abstractions import is_list_type
from .abstract import AbstractView


class BaseView(AbstractView):
    _IGNORE_LIST_BUTTON = False

    def __init__(
        self, 
        state: State,
        filters: Iterable = tuple(),
        extra_keys: Optional[dict[str, str]] = None,
        getter: Optional[DataGetterCallable] = None,
        item_callback_data: Optional[str] = None,
        force_dynamic_keyboard: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs, name_format="{step_name}_view")
        self.item_callback_data = item_callback_data or "ielem"
        self.state = state
        self.filters = filters
        self.callback_data = self._get_callback_data()
        self._extra_keys = extra_keys or self.field.field_info.extra.get('extra_keys')
        self.getter = getter or self.field.field_info.extra.get('getter')
        self.is_static_keyboard = (
            not force_dynamic_keyboard
            and not self._is_state_base_manage 
            and self.getter is None
        )
        self.keyboard_page_size = 10
        self.keyboard = (
            self._build_base_keyboard() 
            if (
                self.is_static_keyboard 
                and self.back_data_getter is None 
            )
            else None
        )
        self.field_name = self.field.field_info.extra.get('short_name') or self.field.name
        self.text = (
            self.field.field_info.extra.get('view_text') 
            or self.view_text_format
        ).format(
            field_name=self.field_name,
            separator=self._text_seperator_symbol[-1]
        )

        logger.debug(f"[{self.__class__.__name__}][__init__]: {locals()=};")

    @property
    def view_text_format(self):
        return self.dialects.INPUT_STR

    @property
    def extra_keys(self) -> dict[str, str]:
        return (self._extra_keys and self._extra_keys.copy()) or {}

    async def get_dynamic_keyboard(
        self, 
        state: FSMContext, 
        page: int = 1, 
        builder: Optional[InlineKeyboardBuilder] = None, 
        back_cq = None,
        **kwargs,
    ):
        builder = builder or InlineKeyboardBuilder()

        if self.getter is not None:
            for data, text in (await self.getter(state, page, self.keyboard_page_size)).items():
                cd = f"{self.item_callback_data}:{data}"
                builder.button(
                    text=text, 
                    callback_data=cd,
                )


        if not back_cq and self._is_state_base_manage:
            state_data = await state.get_data()
            back_cq = state_data.pop('cback_cq', None)

        return self._build_base_keyboard(builder, back_cq=back_cq, **kwargs)

    def _build_base_keyboard(self, builder: Optional[InlineKeyboardBuilder] = None, *, back_cq = None, ignore_list: Optional[bool] = None):
        builder = builder or InlineKeyboardBuilder()

        for data, text in self.extra_keys.items():
            if str(data).lower().startswith(f'{self.item_callback_data}:http') and (ls := str(text).split('*')) and len(ls) > 1:
                builder.button(text=ls[0], url=ls[-1])
            else:
                builder.button(text=text, callback_data=data)

        if not self.field.required:
            builder.button(
                text=self.dialects.SKIP_BUTTON,
                callback_data=f"{self.base_cq_prefix}_{self.dialects.SKIP_STEP_DATA}",
            )

        ignore_list = ignore_list if ignore_list is not None else self._IGNORE_LIST_BUTTON

        if is_list_type(self.field.outer_type_) and not ignore_list:
            builder.button(
                text=self.dialects.READY_BUTTON, 
                callback_data=self.dialects.READY_BUTTON_DATA, 
            )

        back_cq = back_cq or (
            self.back_allowed 
            and (
                (
                    self.is_has_back
                    and f"{self.base_cq_prefix}_{self.dialects.BACK_BUTTON_DATA}"
                )
                or self.back_data 
            )
        )

        if back_cq:
            builder.button(
                text=self.dialects.BACK_BUTTON, 
                callback_data=back_cq,
            )

        return builder.adjust(1)

    def _get_callback_data(self) -> str:
        top_levels = '.'.join(self.parents or tuple())
        return f"{top_levels}.{self.field.name}"

    def register2router(self, router: Router) -> Router:
        router.callback_query(F.data.startswith(self.callback_data), *self.filters)(self.__call__)

        logger.debug(f"[{self.__class__.__name__}][register2router]: {locals()=};")
        return router

    async def __call__(self, self_: THandler, event, state: FSMContext, **kwargs) -> Any:
        event = Event(event)
        res = await self.main(self_, event, state, **kwargs)
        await self._set_current_step(state)
        return res

    async def _set_current_step(self, state: FSMContext):
        await state.update_data(__step__=self.step_name)

    async def main(self, self_: THandler, event: Event, state: FSMContext, **kwargs) -> Any:
        reply_markup=(  # type: ignore
            self.keyboard if self.keyboard
            else await self.get_dynamic_keyboard(state, **kwargs)
        ).as_markup()

        if not reply_markup or not reply_markup.inline_keyboard:  # type: ignore
            reply_markup = None

        await self._show_view(event, state, self.text, reply_markup)

    async def _show_view(self, event: Event, state: FSMContext, text: str, reply_markup=None):
        res = await event.answer(
            text=text, 
            state=state, 
            reply_markup=reply_markup,  # type: ignore
        )

        if isinstance(res, Message):
            await self._set_last_view_msg(res, state)

        await state.set_state(self.state)

    async def _set_last_view_msg(self, message: Message, state: FSMContext):
        await state.update_data(__last_view_msg_id__=message.message_id)

    async def _get_last_view_msg_id(self, state_data: dict):
        return state_data.get('__last_view_msg_id__')

    @classmethod
    def create(cls, field: ModelField, **kwargs) -> 'BaseView':
        logger.debug(f"[{cls.__name__}][create]: {field.name=};")
        return cls(field=field, **kwargs)

