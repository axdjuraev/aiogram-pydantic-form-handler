from types import MethodType
from aiogram import F, Router, types
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from pydantic_base_aiogram.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_base_aiogram.types import Event

from .base import BaseEnumController


class MultipleValueEnumController(BaseEnumController):
    async def item_selected_handler(self, self_: THandler, cq: types.CallbackQuery, state: FSMContext):
        key = self._get_pressed_key_by_data(cq.data, cq.message.reply_markup)  # type: ignore

        if key.text.startswith('+'):
            key.text = key.text[2:]
        else:
            key.text = f"+ {key.text}"

        await cq.message.edit_reply_markup(reply_markup=cq.message.reply_markup)  # type: ignore

    async def ready(self, self_: THandler, cq: types.CallbackQuery, state: FSMContext):
        selected_keys = self._get_selections_by_text_symbol(cq.message.reply_markup, '+')  # type: ignore
        selections = tuple(map(lambda key: self._validate_data(str(key.callback_data).split(':')[1]), selected_keys))

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

