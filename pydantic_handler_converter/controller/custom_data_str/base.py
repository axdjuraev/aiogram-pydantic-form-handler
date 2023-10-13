from pydantic_handler_converter.controller.enum.base import BaseEnumController


class BaseCustomDataController(BaseEnumController):
    def _validate_data(self, data):
        return data

