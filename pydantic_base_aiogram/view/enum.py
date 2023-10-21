from pydantic.fields import ModelField

from pydantic_base_aiogram.types import DescriptiveEnum
from .base import BaseView


class EnumView(BaseView):
    def __init__(self, field: ModelField, *args, is_string_allowed: bool = False, **kwargs) -> None:
        self.is_string_allowed = is_string_allowed
        super().__init__(field=field, *args, **kwargs)

    @property
    def view_text_format(self):
        return self.dialects.CHOOSE_FROM_ENUM if not self.is_string_allowed else self.dialects.CHOOSE_FROM_ENUM_OR_INPUT

    @property
    def extra_keys(self) -> dict[str, str]:
        res = super().extra_keys

        for item in self.field.type_._member_map_.values():
            res[f"{self.item_callback_data}:{item.name}"] = (
                str(item.value) if not isinstance(item, DescriptiveEnum) 
                else item.description
            )

        return res

