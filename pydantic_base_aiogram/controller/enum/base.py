from abc import abstractmethod
from aiogram import F, Router, types
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from pydantic.fields import ModelField
from pydantic_base_aiogram.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_base_aiogram.types import Event

from ..base import BaseController


class BaseCQCheckboxController(BaseController):
    def __init__(self, field: ModelField, *args, is_string_allowed: bool = False, **kwargs) -> None:
        super().__init__(field=field, *args, **kwargs)
        self.is_string_allowed = is_string_allowed

    async def format_data(self, self_: THandler, event: Event, state: FSMContext):
        if isinstance(event._event, types.Message):
            if not self.is_string_allowed or not event._event.text:
                return await event.answer(self.dialects.CONTENT_TYPE_NOT_ALLOWED) 
            return event._event.text
            
        return await self.item_selected_handler(self_, event, state) 

    def _validate_data(self, data):
        return getattr(self.field.type_, data)

    def register2router(self, router: Router) -> Router:
        router.callback_query(StateFilter(self.state), F.data.startswith(self.item_callback_data))(self.__call__)
        return super().register2router(router)
    
    @abstractmethod
    async def item_selected_handler(self, _: THandler, event: Event[types.CallbackQuery], state: FSMContext):
        raise NotImplementedError

