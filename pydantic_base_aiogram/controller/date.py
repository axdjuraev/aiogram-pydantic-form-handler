from datetime import datetime
from typing import Any, Optional
from aiogram.fsm.context import FSMContext

from aiogram.types import Message
from pydantic_base_aiogram.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_base_aiogram.types import Event

from .base import BaseController


class DateController(BaseController):
    def __init__(self, *args, date_format: Optional[str] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.date_format = date_format or "%Y-%m-%d"

    async def main(self, self_: THandler, event: Message, state: FSMContext) -> Any:
        try:
            res = datetime.strptime(str(event.text), self.date_format).date()
        except ValueError:
            return await event.delete()
        await self._setvalue(res, state)
        await self_.next(Event(event), state, self.step_name)  # type: ignore

