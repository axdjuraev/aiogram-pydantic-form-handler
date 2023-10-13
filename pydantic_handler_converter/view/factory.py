from abc import ABC
from typing import Iterable, Optional, Type
from pydantic import BaseModel
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

    def create_by_schema(self, schema: Type[BaseModel], **kwargs):
        views = []

        for field in schema.__fields__.values():
            kwargs['back_data'] = (views or None) and views[-1].callback_data
            res = self.create(field, **kwargs)

            if isinstance(res, Iterable):
                views.extend(res)
            else:
                views.append(res)

        return views

    def create(self, field: ModelField, states: StatesGroup, parents: Optional[Iterable[str]] = None, **kwargs) -> Iterable[BaseView]:
        return super().create(field, states, parents, **kwargs)

