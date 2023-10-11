from aiogram.fsm.context import FSMContext

from pydantic_handler_converter.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_handler_converter.types import Event
from .base import BaseView


class StrView(BaseView):
    async def main(self, _: THandler, event: Event, state: FSMContext):
        await event.answer(self.dialects.INPUT_STR.format(field_name=self.field.name), reply_markup=self.keyboard)
        await state.set_state(self.state)

