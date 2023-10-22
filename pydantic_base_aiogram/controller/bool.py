from aiogram.types import CallbackQuery
from pydantic_base_aiogram.exceptions import DataValidationError
from pydantic_base_aiogram.types import Event
from pydantic_base_aiogram.controller.cq_checkbox.single import SingleCQCheckboxController


class BoolController(SingleCQCheckboxController):
    def _validate_data(self, data):
        try:
            return str(data).strip() == "1"
        except IndexError:
            raise DataValidationError(self.dialects.INVALID_TYPE_DATA)

