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
        self.is_string_allowed = is_string_allowed
        super().__init__(field=field, *args, **kwargs)
        self.text = self.dialects.CHOOSE_FROM_ENUM if not self.is_string_allowed else self.dialects.CHOOSE_FROM_ENUM_OR_INPUT
        self.text = self.text.format(field_name=self.field_name)

    def _enum2dict(self, enum: Type[Enum]) -> dict:
        res = {}
        for item in enum._member_map_.values():
            res[item.name] = (
                item.value if not isinstance(item, DescriptiveEnum) 
                else item.description
            )

        return res

    def _get_keyboard(self, builder: Optional[InlineKeyboardBuilder] = None):
        builder = builder or InlineKeyboardBuilder()

        for name, description in self._enum2dict(self.field.type_).items():
            builder.button(text=description, callback_data=f"{self.item_callback_data}:{name}")

        return super()._get_keyboard(builder)

