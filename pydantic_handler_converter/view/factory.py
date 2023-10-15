from abc import ABC
from typing import Iterable, Type
from pydantic import BaseModel
from pydantic.fields import ModelField
from enum import Enum

from pydantic_handler_converter.field_factory import FieldFactory, logger
from .string import StrView
from .float import FloatView
from .int import IntView
from .enum import EnumView
from .models import ModelsView


class ViewFactory(FieldFactory, ABC):
    CONVERT_DIALECTS = {
        str: StrView,
        int: IntView,
        float: FloatView,
        Enum: EnumView,
    }

    def create_by_schema(self, schema: Type[BaseModel], **kwargs):
        super().create_by_schema
        views = []
        logger.debug(f"[{self.__class__.__name__}][create_by_schema]: {locals()=}")

        for index, field in enumerate(schema.__fields__.values()):
            kwargs['is_has_back'] = bool(views) if index > 0 else kwargs.get('is_has_back', False)
            res = self.create(field=field, **kwargs)

            if isinstance(res, Iterable):
                views.extend(res)
            else:
                views.append(res)

        return views

    def create4models(self, field: ModelField, models: list[Type[BaseModel]], kwargs: dict):
        views = []
        models_dialects = {}

        for tree_id, model in enumerate(models, start=1):
            logger.debug(f"[{self.__class__.__name__}][create4models]: {locals()=}")
            model_views = self.create_by_schema(model, tree_id=tree_id, tree_head_field=field, **kwargs)

            if model_views:
                models_dialects[model] = model_views[0]
                views.extend(model_views)
        
        views.insert(0, ModelsView.create(field=field, models_dialects=models_dialects, **kwargs))

        return views

