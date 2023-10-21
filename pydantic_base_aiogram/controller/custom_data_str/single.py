from pydantic_base_aiogram.controller.enum.single import SingleValueEnumController

from .base import BaseCustomDataController


class SingleValueCustomDataController(SingleValueEnumController, BaseCustomDataController):
    pass

