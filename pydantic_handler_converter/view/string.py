from typing import Optional
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from pydantic_handler_converter.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_handler_converter.types import Event, DataGetterCallable, GetterField, ExtraStringField
from .base import BaseView


class StrView(BaseView):
    async def main(self, _: THandler, event: Event, state: FSMContext):
        await event.answer(self.dialects.INPUT_STR.format(field_name=self.field.name), reply_markup=self.keyboard.as_markup())
        await state.set_state(self.state)
    
    @classmethod
    def create(cls, field, **kwargs) -> 'BaseView':
        if isinstance(field, GetterField):
            is_extra_str = False if not isinstance(field.outer_type_, ExtraStringField) else field.outer_type_.is_extra_str
            return CustomDataStrView(field=field, getter=field.getter, is_extra_str=is_extra_str, **kwargs)

        return super().create(field, **kwargs)


class CustomDataStrView(BaseView):
    def __init__(self, *args, getter: DataGetterCallable, is_extra_str: bool = False, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.getter = getter
        self.is_extra_str = is_extra_str
        self.text = self.dialects.CHOOSE_FROM_LIST_OR_INPUT if is_extra_str else self.dialects.CHOOSE_FROM_LIST
        self.text = self.text.format(field_name=self.field.name)

    async def _get_keyboard(self, builder: Optional[InlineKeyboardBuilder] = None):
        builder = builder or InlineKeyboardBuilder()
        elems = await self.getter()

        for elem in elems:
            builder.button(text=elem.text, callback_data=elem.data)

        return super()._get_keyboard(builder)

    async def main(self, _: THandler, event: Event, state: FSMContext):
        await event.answer(self.text, reply_markup=(await self._get_keyboard()).as_markup())
        await state.set_state(self.state)

