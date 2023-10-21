from pydantic_base_aiogram.controller.enum.base import BaseEnumController


class BaseCustomDataController(BaseEnumController):
    def _validate_data(self, data):
        return data

