
from aiogram.types import Message
from pydantic_base_aiogram.controller.cq_checkbox.multiple import MultipleCQCheckboxController
from pydantic_base_aiogram.types import Event
from .base import BaseCustomDataController


class MultipleValueCustomDataController(MultipleCQCheckboxController, BaseCustomDataController):
    pass

