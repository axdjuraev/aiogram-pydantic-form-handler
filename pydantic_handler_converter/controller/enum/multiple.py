from aiogram import types
from aiogram.fsm.context import FSMContext
from pydantic_handler_converter.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_handler_converter.types import Event

from .base import BaseEnumController


class MultipleValueEnumController(BaseEnumController):
    async def item_selected_handler(self, self_: THandler, cq: types.CallbackQuery, state: FSMContext):
        _, value = str(cq.data).split(":")
        await self._setvalue(value, state)
        return await self_.next(Event(cq), state, self.step_name)  # type: ignore

