from abc import ABC
from typing import Iterable, Optional, Type
from pydantic import BaseModel
from pydantic.fields import ModelField
from enum import Enum

from pydantic_base_aiogram.field_factory import FieldFactory, logger
from pydantic_base_aiogram.utils.step import get_step_name
from .string import StrView
from .float import FloatView
from .int import IntView
from .enum import EnumView
from .models import ModelsView
from .bool import BoolView


class ViewFactory(FieldFactory, ABC):
    CONVERT_DIALECTS = {
        str: StrView,
        int: IntView,
        float: FloatView,
        Enum: EnumView,
        bool: BoolView,
    }

    def create_by_schema(self, schema: Type[BaseModel], _except_steps: Optional[Iterable] = None, **kwargs):
        views = []
        logger.debug(f"[{self.__class__.__name__}][create_by_schema]: {locals()=}")

        for field in schema.__fields__.values():
            kwargs['is_has_back'] = bool(len(views))

            if kwargs['is_has_back']:
                kwargs['back_data'] = None

            res = self.create(field=field, **kwargs)

            if isinstance(res, Iterable):
                views.extend(res)
            elif res is not None:
                views.append(res)

        return views

    def create4models(self, field: ModelField, models: list[Type[BaseModel]], kwargs: dict):
        views = []
        models_dialects = {}
        tree_head_step_name = get_step_name(field, kwargs['parents'])
        ignore_list = kwargs.get('_except_steps', tuple())

        for tree_id, model in enumerate(models, start=1):
            logger.debug(f"[{self.__class__.__name__}][create4models]: {locals()=}")
            model_views = self.create_by_schema(model, tree_id=tree_id, tree_head_step_name=tree_head_step_name, **kwargs)
            model_views = tuple(filter(lambda x: x.step_name not in ignore_list, model_views))

            if model_views:
                models_dialects[model] = model_views[0]
                views.extend(model_views)

        views.insert(0, ModelsView.create(field=field, models_dialects=models_dialects, **kwargs))

        return views

