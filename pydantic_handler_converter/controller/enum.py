from pydantic.fields import ModelField
from .base import BaseController


class EnumController(BaseController):
    def __init__(self, field: ModelField, *args, is_string_allowed: bool = False, **kwargs) -> None:
        self.item_callback_data = None
        self.is_string_allowed = is_string_allowed
        super().__init__(field, *args, **kwargs)

    # async def main(self, _: THandler, event: Event, state: FSMContext):
    async def main(self):
        raise NotImplementedError

