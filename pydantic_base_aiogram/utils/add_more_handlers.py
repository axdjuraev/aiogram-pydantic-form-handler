from uuid import uuid4
from typing import Awaitable, Callable, Optional, Union
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from pydantic_base_aiogram.dialecsts import BaseDialects
from pydantic_base_aiogram.types import Event


class AddMoreHandlers:
    def __init__(
        self, 
        next_handler: Callable[[Event, FSMContext, int], Awaitable],
        dialects: BaseDialects,
        cb_data_prefix: Optional[str] = None,
        default_back_data: Optional[str] = None,
    ) -> None:
        self._next_handler = next_handler
        self._dialects = dialects
        self._builder = InlineKeyboardBuilder()
        self._cb_data_prefix = cb_data_prefix or str(uuid4())
        self._default_back_data = default_back_data

    def _get_keyboard_builder(self, back_data: Optional[str] = None) -> InlineKeyboardBuilder:
        builder = InlineKeyboardBuilder()
        builder.button(text=self._dialects.BOOL_CHOICE_YES, callback_data=f"{self._cb_data_prefix}:1")
        builder.button(text=self._dialects.BOOL_CHOICE_NO, callback_data=f"{self._cb_data_prefix}:0")

        back_data = back_data or self._default_back_data

        if back_data:
            builder.button(
                text=self._dialects.BACK_BUTTON, 
                callback_data=f"{self._cb_data_prefix}:{self._dialects.BACK_BUTTON_DATA}"
            )

        builder.adjust(1)
        return builder

    async def view(self, update: Union[types.Message, types.CallbackQuery], back_data: Optional[str] = None) -> None:
        event = Event(update)
        keyboard = self._get_keyboard_builder(back_data)
        await event.answer(self._dialects.ADD_MORE, reply_markup=keyboard.as_markup())

    async def contorller(self, cq: types.CallbackQuery, state: FSMContext) -> None:
        choice = int(str(cq.data).split(":")[-1])
        await self._next_handler(Event(cq), state, choice)

    def register2router(self, router: Router) -> Router:
        router.callback_query(F.data.startswith(self._cb_data_prefix))(self.contorller)

        return router

