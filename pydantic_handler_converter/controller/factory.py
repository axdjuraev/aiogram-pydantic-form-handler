from abc import ABC
from typing import Iterable, Optional
from pydantic.fields import ModelField
from aiogram.fsm.state import StatesGroup
from enum import Enum

from pydantic_handler_converter.field_factory import FieldFactory
from .string import StrController
from .float import FloatController
from .int import IntController
from .enum import EnumController


class ControllerFactory(FieldFactory, ABC):
    CONVERT_DIALECTS = {
        str: StrController,
        int: IntController,
        float: FloatController,
        Enum: EnumController,
    }

    def create(self, field: ModelField, states: StatesGroup, parents: Optional[Iterable[str]] = None, **kwargs):
        return super().create(field, states, parents, **kwargs)

