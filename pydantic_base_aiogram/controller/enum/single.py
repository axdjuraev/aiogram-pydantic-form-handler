from aiogram import types
from aiogram.fsm.context import FSMContext
from pydantic_base_aiogram.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_base_aiogram.types import Event

from .base import BaseEnumController


class SingleValueEnumController(BaseEnumController):
    async def item_selected_handler(self, self_: THandler, cq: types.CallbackQuery, state: FSMContext):
        _, value = str(cq.data).split(":")
        await self._setvalue(self._validate_data(value), state)
        return await self_.next(Event(cq), state, self.step_name)  # type: ignore

