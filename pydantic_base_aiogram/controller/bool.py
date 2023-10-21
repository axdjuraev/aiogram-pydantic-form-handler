from aiogram.types import CallbackQuery
from pydantic_base_aiogram.exceptions import DataValidationError
from pydantic_base_aiogram.types import Event
from .base import BaseController


class BoolController(BaseController):
    async def format_data(self, self_, event: Event[CallbackQuery], *_):
        try:
            return str(event._event.data).split(':')[1].strip() == "1"
        except IndexError:
            raise DataValidationError(self.dialects.INVALID_TYPE_DATA)

