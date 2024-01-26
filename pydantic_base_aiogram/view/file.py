from aiogram import Router
from aiogram.filters.state import StateFilter

from pydantic_base_aiogram.types import Event
from .base import BaseView


class FileView(BaseView):
    _IGNORE_LIST_BUTTON = True

    @property
    def view_text_format(self):
        if self._is_list:
            return self.dialects.SEND_FILES

        return self.dialects.SEND_FILE
    
    async def add_more_view(self, event_type, state):
        event = Event(event_type)
        keyboard = await self.get_dynamic_keyboard(state, ignore_list=False)
        await event.answer(
            self.dialects.WAITING_EXTRA_FILES, 
            reply_markup=keyboard.as_markup(), # type: ignore
        )

    def register2router(self, router: Router) -> Router:
        router.message(StateFilter(self.state))(self.add_more_view)
        return super().register2router(router)

