from abc import ABC
from typing import Iterable, Type
from pydantic import BaseModel
from pydantic.fields import ModelField
from enum import Enum

from pydantic_base_aiogram.field_factory import FieldFactory, logger
from .string import StrView
from .float import FloatView
from .int import IntView
from .enum import EnumView
from .models import ModelsView
from .bool import BoolView
from .file import FileView


class ViewFactory(FieldFactory, ABC):
    CONVERT_DIALECTS = {
        str: StrView,
        int: IntView,
        float: FloatView,
        Enum: EnumView,
        bool: BoolView,
        bytes: FileView,
    }

    def create_by_schema(self, schema: Type[BaseModel], **kwargs):
        views = []
        logger.debug(f"[{self.__class__.__name__}][create_by_schema]: {locals()=}")

        for field in schema.__fields__.values():
            kwargs['is_has_back'] = bool(len(views)) or kwargs.get('is_has_back', False)

            if kwargs['is_has_back']:
                kwargs['back_data'] = None

            if not kwargs.get('tree_head_step_name') and views:
                kwargs['tree_head_step_name'] = views[-1].step_name

            res = self.create(field=field, **kwargs)

            if isinstance(res, Iterable):
                views.extend(res)
            elif res is not None:
                views.append(res)

        return views

    def create4models(self, field: ModelField, models: list[Type[BaseModel]], kwargs: dict):
        views, models_dialects = super().create4models(field, models, kwargs)
        views.insert(0, ModelsView.create(field=field, models_dialects=models_dialects, **kwargs))
        return views

