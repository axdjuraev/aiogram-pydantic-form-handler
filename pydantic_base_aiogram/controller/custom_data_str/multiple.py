from pydantic_base_aiogram.controller.enum.multiple import MultipleValueEnumController
from .base import BaseCustomDataController


class MultipleValueCustomDataController(MultipleValueEnumController, BaseCustomDataController):
    pass

