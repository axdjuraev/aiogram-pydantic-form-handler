from aiogram import Router
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext

from pydantic_base_aiogram.types import Event
from .base import BaseView


class FileView(BaseView):
    _IGNORE_LIST_BUTTON = True

    @property
    def view_text_format(self):
        if self._is_list:
            return self.dialects.SEND_FILES

        return self.dialects.SEND_FILE
    
    async def add_more_view(self, event: Event, state: FSMContext):
        state_data = await state.get_data()

        if (last_view_messsage_id := await self._get_last_view_msg_id(state_data)):
            try:
                await state.bot.edit_message_reply_markup(
                    chat_id=state.key.chat_id,
                    message_id=last_view_messsage_id, 
                    reply_markup=None,
                )
            except Exception:
                pass
        
        keyboard = await self.get_dynamic_keyboard(state, ignore_list=False)
        await self._show_view(event, state, self.dialects.WAITING_EXTRA_FILES, keyboard.as_markup())

    def register2router(self, router: Router) -> Router:
        router.message(StateFilter(self.state))(self.add_more_view)
        return super().register2router(router)

