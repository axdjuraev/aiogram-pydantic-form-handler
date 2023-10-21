from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from pydantic_base_aiogram.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_base_aiogram.types import Event
from pydantic_base_aiogram.exceptions import DataValidationError

from .base import BaseController


class TypeBaseMessageTextController(BaseController):
    async def __call__(self, self_: THandler, event, state: FSMContext):
        if not isinstance(event, Message):
            raise DataValidationError(self.dialects.INVALID_TYPE_DATA)

        return await self.main(self_, Event(event), state)

    async def format_data(self, self_: THandler, event: Event[Message], state: FSMContext):
        try:
            return self.field.type_(event._event.text)
        except ValueError:
            raise DataValidationError(self.dialects.INVALID_TYPE_DATA)

