from pydantic_handler_converter.controller.enum.base import BaseEnumController


class BaseCustomDataController(BaseEnumController):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.item_callback_data = "ielem"

    def _validate_data(self, data):
        return data

