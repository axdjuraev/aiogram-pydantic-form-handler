from pydantic_base_aiogram.utils.abstractions import is_list_type
from .base import BaseView


class StrView(BaseView):
    _IGNORE_LIST_BUTTON = True

    @property
    def view_text_format(self):
        return (
            self.dialects.INPUT_STR_LIST if is_list_type(self.field.outer_type_)
            else self.dialects.INPUT_STR
        )

    @classmethod
    def create(cls, field, **kwargs) -> 'BaseView':
        if getter := field.field_info.extra.get('getter'):
            is_extra_str = field.field_info.extra.get('is_extra_str', False)
            return CustomDataStrView(field=field, getter=getter, is_extra_str=is_extra_str, **kwargs)

        return super().create(field=field, **kwargs)


class CustomDataStrView(BaseView):
    def __init__(self, *args, is_extra_str: bool = False, **kwargs) -> None:
        self.is_extra_str = is_extra_str
        super().__init__(*args, **kwargs)

    @property
    def view_text_format(self):
        return (
            self.dialects.CHOOSE_FROM_LIST_OR_INPUT if self.is_extra_str 
            else self.dialects.CHOOSE_FROM_LIST
        )

