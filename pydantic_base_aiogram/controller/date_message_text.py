from datetime import datetime
from typing import Optional
from aiogram.fsm.context import FSMContext

from aiogram.types import Message
from pydantic_base_aiogram.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_base_aiogram.exceptions import DataValidationError
from pydantic_base_aiogram.types import Event

from .type_base_message_text import TypeBaseMessageTextController


class DateMessageTextController(TypeBaseMessageTextController):
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, *args, date_format: Optional[str] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.date_format = date_format or self.DATE_FORMAT

    async def format_data(self, self_: THandler, event: Event[Message], state: FSMContext):
        try:
            return datetime.strptime(str(event._event.text), self.date_format).date()
        except ValueError:
            raise DataValidationError(self.dialects.INVALID_TYPE_DATA)

