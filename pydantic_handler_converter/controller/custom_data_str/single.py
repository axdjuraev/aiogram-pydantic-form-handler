from pydantic_handler_converter.controller.enum.single import SingleValueEnumController

from .base import BaseCustomDataController


class SingleValueCustomDataController(SingleValueEnumController, BaseCustomDataController):
    pass

