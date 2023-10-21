from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from pydantic_base_aiogram.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_base_aiogram.types import Event
from pydantic_base_aiogram.exceptions import DataValidationError

from .base import BaseController


class TypeBaseMessageTextController(BaseController):
    async def format_data(self, self_: THandler, event: Event, state: FSMContext):
        try:
            if not isinstance(event._event, Message):
                raise DataValidationError(self.dialects.INVALID_TYPE_DATA)

            return self.field.type_(event._event.text)
        except ValueError:
            raise DataValidationError(self.dialects.INVALID_TYPE_DATA)

