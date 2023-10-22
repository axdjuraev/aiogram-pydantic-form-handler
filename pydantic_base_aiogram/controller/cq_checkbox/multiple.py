from types import MethodType
from typing import Optional
from aiogram import F, Router, types
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pydantic_base_aiogram.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_base_aiogram.types import Event

from .base import BaseCQCheckboxController


class MultipleCQCheckboxController(BaseCQCheckboxController):
    SELECTION_SYMBOL = '+'

    def __init__(self, field, *args, selection_symbol: Optional[str] = None, **kwargs) -> None:
        super().__init__(field, *args, **kwargs)
        self.selection_symbol = selection_symbol or self.SELECTION_SYMBOL
        self.selection_symbol_length = len(self.selection_symbol)

    async def item_selected_handler(self, _: THandler, event: Event[types.CallbackQuery], state: FSMContext):
        key = self._get_pressed_key_by_data(event._event.data, event._event.message.reply_markup)  # type: ignore

        if key.text.startswith(self.selection_symbol):
            key.text = key.text[(self.selection_symbol_length + 1):]
        else:
            key.text = f"{self.selection_symbol} {key.text}"

        await event._event.message.edit_reply_markup(reply_markup=event._event.message.reply_markup)  # type: ignore
        return ...

    async def ready(self, self_: THandler, cq: types.CallbackQuery, state: FSMContext):
        selected_keys = self._get_selections_by_text_symbol(cq.message.reply_markup, self.selection_symbol)  # type: ignore
        selections = tuple(map(lambda key: self._validate_data(str(key.callback_data).split(self.data_split_symbol)[1]), selected_keys))

        await self._setvalue(selections, state)
        return await self_.next(Event(cq), state, self.step_name)  # type: ignore

    def _get_selections_by_text_symbol(self, keyboard: InlineKeyboardMarkup, symbol: str) -> list[InlineKeyboardButton]:
        choosens = []

        if not keyboard:
            raise NotImplementedError

        for row in keyboard.inline_keyboard:
            for key in row:
                if not key.text.startswith(symbol):
                    continue
                choosens.append(key)

        return choosens

    def _get_pressed_key_by_data(self, data: str, keyboard: InlineKeyboardMarkup):
        for row in keyboard.inline_keyboard:
            for key in row:
                if key.callback_data == data:
                    return key

        raise NotImplementedError

    def bind(self, elem):
        super().bind(elem)
        self.ready = MethodType(self.ready, elem)

    def register2router(self, router: Router) -> Router:
        router.callback_query(StateFilter(self.state), F.data == self.dialects.READY_BUTTON_DATA)(self.ready)
        return super().register2router(router)

