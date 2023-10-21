from collections.abc import Iterable
from typing import Optional, Type

from pydantic import BaseModel
from pydantic.fields import ModelField
from .base import BaseFieldFactory, logger


class ModelFieldFactory(BaseFieldFactory):
    def create_by_schema(self, schema: Type[BaseModel], **kwargs):
        views = []

        for field in schema.__fields__.values():
            res = self.create(field=field, **kwargs)

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
        return self.create_by_schema(field.type_, parents=parents, **kwargs, states=states) 

