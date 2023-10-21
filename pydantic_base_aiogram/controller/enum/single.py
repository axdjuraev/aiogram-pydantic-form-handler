from aiogram import types
from aiogram.fsm.context import FSMContext
from pydantic_base_aiogram.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_base_aiogram.exceptions import DataValidationError
from pydantic_base_aiogram.types import Event

from .base import BaseCQCheckboxController


class SingleCQCheckboxController(BaseCQCheckboxController):
    async def item_selected_handler(self, _: THandler, event: Event[types.CallbackQuery], state: FSMContext):
        try:
             return str(event._event.data).split(":")[1]
        except IndexError:
            raise DataValidationError(self.dialects.INVALID_TYPE_DATA)

