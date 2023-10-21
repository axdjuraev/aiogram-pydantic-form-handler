from typing import Optional

from aiogram.utils.keyboard import InlineKeyboardBuilder
from .base import BaseView 


class BoolView(BaseView):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.text = (
            self.field.field_info.extra.get('view_text') 
            or self.dialects.CHOOSE_FROM_LIST.format(field_name=self.field_name)
        )

    def _get_keyboard(self, builder: Optional[InlineKeyboardBuilder] = None):
        builder = builder or InlineKeyboardBuilder()

        builder.button(
            text=self.dialects.BOOL_CHOICE_YES,
            callback_data=f"{self.item_callback_data}:1",
        )
        builder.button(
            text=self.dialects.BOOL_CHOICE_NO,
            callback_data=f"{self.item_callback_data}:0",
        )

        return super()._get_keyboard(builder)

