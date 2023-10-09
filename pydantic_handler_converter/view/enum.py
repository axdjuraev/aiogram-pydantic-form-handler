from enum import Enum
from typing import Optional, Type
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pydantic.fields import ModelField

from pydantic_handler_converter.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_handler_converter.types import Event, DescriptiveEnum
from .base import BaseView


class EnumView(BaseView):
    def __init__(self, field: ModelField, *args, is_string_allowed: bool = False, **kwargs) -> None:
        self.item_callback_data = None
        self.is_string_allowed = is_string_allowed
        super().__init__(field, *args, **kwargs)

    def _enum2dict(self, enum: Type[Enum]) -> dict:
        res = {}
        for item in enum._member_map_.values():
            res[item.name] = (
                item.value if not isinstance(item, DescriptiveEnum) 
                else item.description
            )

        return res

    def _get_keyboard(self, builder: Optional[InlineKeyboardBuilder] = None):
        if self.item_callback_data is None:
            self.item_callback_data = f"elem_{self.callback_data}"

        builder = builder or InlineKeyboardBuilder()

        for name, description in self._enum2dict(self.field.type_).items():
            builder.button(text=description, data=f"{self.item_callback_data}:{name}")

        return super()._get_keyboard(builder)

    async def main(self, _: THandler, event: Event, state: FSMContext):
        text = self.dialects.CHOOSE_FROM_ENUM if not self.is_string_allowed else self.dialects.CHOOSE_FROM_ENUM_OR_INPUT
        await event.answer(text.format(field_name=self.field.name), reply_markup=self.keyboard)
        await state.set_state(self.state)

