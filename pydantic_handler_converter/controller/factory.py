from abc import ABC
from typing import Iterable, Optional, Type, Union
from pydantic import BaseModel
from pydantic.fields import ModelField
from aiogram.fsm.state import StatesGroup
from enum import Enum

from pydantic_handler_converter.field_factory import FieldFactory
from .string import StrController
from .float import FloatController
from .int import IntController
from .enum import EnumController
from .custom_data_str import CustomDataStrController


class ControllerFactory(FieldFactory, ABC):
    CONVERT_DIALECTS = {
        str: StrController,
        int: IntController,
        float: FloatController,
        Enum: EnumController,
        Union[str, Enum]: CustomDataStrController,
    }

    def create4models(self, _: ModelField, models: list[Type[BaseModel]], kwargs: dict):
        res = []
        
        for model in models:
            res.extend(self.create_by_schema(model, **kwargs))

        return res

    def create(self, field: ModelField, states: StatesGroup, parents: Optional[Iterable[str]] = None, **kwargs):
        return super().create(field, states, parents, **kwargs)

    def create4type(self, field: ModelField, parents: Optional[Iterable[str]] = None, force_type: Optional[type] = None, **kwargs):
        if field.field_info.extra.get('getter'):
            force_type = Union[str, Enum]

        return super().create4type(field, parents, force_type, **kwargs)

