from abc import abstractmethod
from typing import Union
from aiogram import types
from aiogram.fsm.context import FSMContext
from pydantic.fields import ModelField
from pydantic_handler_converter.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_handler_converter.types import Event

from ..base import BaseController


class BaseEnumController(BaseController):
    def __init__(self, field: ModelField, *args, is_string_allowed: bool = False, **kwargs) -> None:
        self.is_string_allowed = is_string_allowed
        super().__init__(field, *args, **kwargs)

    async def __call__(self, self_: THandler, event: Union[types.Message, types.CallbackQuery], state: FSMContext):
        if isinstance(event, types.Message):
            if not self.is_string_allowed:
                return await event.answer(self.dialects.CONTENT_TYPE_NOT_ALLOWED) 
            return await self.message_handler(self_, event, state)
            
        return await self.item_selected_handler(self_, event, state) 

    async def message_handler(self, self_: THandler, message: types.Message, state: FSMContext):
        await self._setvalue(message.text, state)
        return await self_.next(Event(message), state, self.step_name)  # type: ignore
    
    @abstractmethod
    async def item_selected_handler(self, _: THandler, cq: types.CallbackQuery, state: FSMContext):
        raise NotImplementedError

