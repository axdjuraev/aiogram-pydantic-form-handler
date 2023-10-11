from abc import ABC
from typing import Iterable, Optional
from pydantic.fields import ModelField
from aiogram.fsm.state import StatesGroup
from enum import Enum
from pydantic_handler_converter.view.base import BaseView

from pydantic_handler_converter.field_factory import FieldFactory
from .string import StrView
from .float import FloatView
from .int import IntView
from .enum import EnumView


class ViewFactory(FieldFactory, ABC):
    CONVERT_DIALECTS = {
        str: StrView,
        int: IntView,
        float: FloatView,
        Enum: EnumView,
    }

    def create(self, field: ModelField, states: StatesGroup, parents: Optional[Iterable[str]] = None, **kwargs) -> Iterable[BaseView]:
        return super().create(field, states, parents, **kwargs)

