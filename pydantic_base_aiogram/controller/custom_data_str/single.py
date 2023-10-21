from pydantic_base_aiogram.controller.cq_checkbox.single import SingleCQCheckboxController

from .base import BaseCustomDataController


class SingleValueCustomDataController(SingleCQCheckboxController, BaseCustomDataController):
    pass

