from pydantic_base_aiogram.controller.cq_checkbox.base import BaseCQCheckboxController


class BaseCustomDataController(BaseCQCheckboxController):
    def _validate_data(self, data):
        return data

