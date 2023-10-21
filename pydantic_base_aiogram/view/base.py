from typing import Any, Callable, Iterable, Optional, Union
from typing import _GenericAlias, GenericAlias  # type: ignore
from pydantic.fields import ModelField
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State

from pydantic_base_aiogram.types import DataGetterCallable, Event
from pydantic_base_aiogram.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_base_aiogram.field_factory import logger
from .abstract import AbstractView


class BaseView(AbstractView):
    def __init__(
        self, 
        state: State,
        filters: Iterable = tuple(),
        extra_keys: Optional[dict[str, str]] = None,
        getter: Optional[DataGetterCallable] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs, name_format="{step_name}_view")
        self.item_callback_data = "ielem"
        self.state = state
        self.filters = filters
        self.callback_data = self._get_callback_data()
        self.extra_keys = extra_keys
        self.getter = getter
        self.is_static_keyboard = self.getter is None
        self.keyboard = self._build_base_keyboard() if self.is_static_keyboard else None
        self.field_name = self.field.field_info.extra.get('short_name') or self.field.name
        self.text = (
            self.field.field_info.extra.get('view_text') 
            or self.view_text_format.format(field_name=self.field_name)
        )
        logger.debug(f"[{self.__class__.__name__}][__init__]: {locals()=};")

    @property
    def view_text_format(self):
        return self.dialects.INPUT_STR

    def _build_base_keyboard(self, builder: Optional[InlineKeyboardBuilder] = None):
        builder = builder or InlineKeyboardBuilder()

        if self.extra_keys:
            for data, text in self.extra_keys.items():
                builder.button(text=text, callback_data=data)

        if not self.field.required:
            builder.button(
                text=self.dialects.SKIP_BUTTON,
                callback_data=f"{self.base_cq_prefix}_{self.dialects.SKIP_STEP_DATA}",
            )

        logger.debug(f"[{self.__class__.__name__}][_get_keyboard]: {self.is_has_back=}; {locals()=};")
        if self.is_has_back and self.back_allowed:
            builder.button(
                text=self.dialects.BACK_BUTTON, 
                callback_data=f"{self.base_cq_prefix}_{self.dialects.BACK_BUTTON_DATA}",
            )

        if isinstance(self.field.outer_type_, Union[_GenericAlias, GenericAlias]):
            builder.button(
                text=self.dialects.READY_BUTTON, 
                callback_data=self.dialects.READY_BUTTON_DATA, 
            )

        return builder.adjust(1)

    def _get_callback_data(self) -> str:
        top_levels = '.'.join(self.parents or tuple())
        return f"{top_levels}.{self.field.name}"

    def register2router(self, router: Router) -> Router:
        router.callback_query(F.data.startswith(self.callback_data), *self.filters)(self.__call__)

        logger.debug(f"[{self.__class__.__name__}][register2router]: {locals()=};")
        return router

    async def __call__(self, self_: THandler, event, state: FSMContext) -> Any:
        event = Event(event)
        res = await self.main(self_, event, state)
        await self._set_current_step(state)
        return res

    async def _set_current_step(self, state: FSMContext):
        await state.update_data(__step__=self.step_name)

    async def main(self, self_: THandler, event: Event, state: FSMContext) -> Any:
        await event.answer(self.text, state, reply_markup=self.keyboard.as_markup())
        await state.set_state(self.state)

    @classmethod
    def create(cls, field: ModelField, **kwargs) -> 'BaseView':
        logger.debug(f"[{cls.__name__}][create]: {field.name=};")
        return cls(field=field, **kwargs)

