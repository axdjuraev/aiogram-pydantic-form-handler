from abc import ABC
from typing import Any, Iterable, Optional, Type
from aiogram.fsm.state import StatesGroup
from pydantic import BaseModel
from pydantic.fields import ModelField
from axabc.logging import SimpleFileLogger


logger = SimpleFileLogger('aiogram-pydantic-handler')


class BaseFieldFactory(ABC):
    CONVERT_DIALECTS: dict[type, Any] = {}

    def create_by_schema(self, schema: Type[BaseModel], **kwargs):
        views = []

        for field in schema.__fields__.values():
            views.append(self.create(field, **kwargs))

        return views

    def create(self, field: ModelField, parents: Optional[Iterable[str]] = None, **kwargs):
        type_ = field.type_
        base_type_name = type(type_).__name__ 
        logger.debug(f"[{self.__class__.__name__}][create]: {field.name=}; {type_=}; {base_type_name=}")

        try: 
            creator = getattr(self, f'_create_{base_type_name}')
            res = creator(field, kwargs, parents)
            return res if isinstance(res, Iterable) else (res,)
        except AttributeError:
            raise NotImplementedError(f'`{base_type_name}` is not supported in {self.__class__.__name__}')

    def _create_type(self, field: ModelField, kwargs: dict, parents: Optional[Iterable[str]] = None):
        logger.debug(f"[{self.__class__.__name__}][_create_type]: {field.name=}; {parents=};")

        view_cls = self.CONVERT_DIALECTS.get(field.type_)

        if view_cls is None:
            raise NotImplementedError(f'`{field.type_}` is not supported in {self.__class__.__name__}')

        return view_cls.create(field, parents=parents, **kwargs)

    def _create_modelmetaclass(self, field: ModelField, kwargs: dict, parents: Optional[Iterable[str]] = None):
        states = kwargs.pop('states').get(field.name)
        logger.debug(f"[{self.__class__.__name__}][_create_modelmetaclass_view]: {field.name=}; {parents=}; {kwargs=};")
        parents = (*parents, field.name) if parents else (field.name,)
        return self.create_by_schema(field.type_, parents=parents, **kwargs, states=states) 

