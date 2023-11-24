from aiogram.types import Message
from pydantic_base_aiogram.types import Event
from .base import BaseController


class FileController(BaseController):
    async def format_data(self, self_, event: Event[Message], state):
        return await super().format_data(self_, event, state)
