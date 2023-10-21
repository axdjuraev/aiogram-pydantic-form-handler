from typing import Optional

from aiogram.utils.keyboard import InlineKeyboardBuilder
from .base import BaseView 


class BoolView(BaseView):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _choice_keys(self, builder: Optional[InlineKeyboardBuilder] = None):
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

