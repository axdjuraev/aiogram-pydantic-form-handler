from collections.abc import Iterable
from typing import Optional, Type

from pydantic import BaseModel
from pydantic.fields import ModelField

from pydantic_base_aiogram.utils.abstractions import is_list_type
from .base import BaseFieldFactory, logger


class ModelFieldFactory(BaseFieldFactory):
    def create_by_schema(self, schema: Type[BaseModel], *, is_list_item: bool = False, **kwargs):
        views = []

        for field in schema.__fields__.values():
            res = self.create(field=field, is_list_item=is_list_item, **kwargs)

            if isinstance(res, Iterable):
                if (ignore_list := kwargs.get('_except_steps')) is not None:
                    res = filter(lambda x: x.step_name not in ignore_list, res)

                views.extend(res)
            elif res is not None:
                views.append(res)

        return views

    def create4modelmetaclass(self, field: ModelField, parents: Optional[Iterable[str]] = None, **kwargs):
        kwargs.pop('state')
        states = getattr(kwargs.pop('states'), field.name)
        logger.debug(f"[{self.__class__.__name__}][_create_modelmetaclass_view]: {field.name=}; {parents=}; {kwargs=};")
        parents = (*parents, field.name) if parents else (field.name,)
        is_list_item = is_list_type(field.outer_type_)

        if 'is_list_item' in kwargs:
            del kwargs['is_list_item']

        res = self.create_by_schema(
            field.type_, 
            parents=parents, 
            states=states,
            is_list_item=is_list_item,
            **kwargs, 
        ) 

        return res

