from abc import ABC
from itertools import chain
from typing import Any, Iterable, Optional, Type, Union 
from aiogram.fsm.state import StatesGroup
from enum import Enum
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

    def create(self, field: ModelField, states: StatesGroup, parents: Optional[Iterable[str]] = None, **kwargs):
        type_ = field.type_
        base_type_name = str(type(type_).__name__).lower()
        logger.debug(f"[{self.__class__.__name__}][create]: {field.name=}; {type_=}; {base_type_name=}")

        try: 
            creator = getattr(self, f'_create_{base_type_name}')
        except AttributeError as e:
            logger.error(str(e))
            raise NotImplementedError(f'`{base_type_name}` is not supported metatype in {self.__class__.__name__}')

        state = getattr(states, field.name)
        res = creator(field, state=state, states=states, **kwargs, parents=parents)
        return res

    def _countup_things(self, field, things: list):
        strs_count = 0
        enums = []
        models = []

        for item in things:
            if issubclass(item, Enum):
                enums.append(item)
            elif issubclass(item, BaseModel):
                models.append(models)
            elif issubclass(item, Union[str, float, int]):
                strs_count += 1
            else:
                raise NotImplementedError(f'`{field.type_}` is too comple type for `{self.__class__.__name__}`')

        return strs_count, enums, models

    def _create__uniongenericalias(self, field: ModelField, parents, **kwargs):
        args = field.type_.__args__
        all_count = len(args)
        strs_count, enums, models = self._countup_things(field, args)

        if strs_count == all_count:
            return self._create_type(field, parents, force_type=str, **kwargs)
        elif all_count == (len(enums) + strs_count):
            combined_name = ''.join(map(lambda x: x.__name__, enums))
            field.type_ = Enum(combined_name, [(x.name, x.value) for x in chain(*enums)])
            return self._create_enummeta(field, parents, is_string_allowed=strs_count > 0, **kwargs)
        elif strs_count or len(enums):
            raise NotImplementedError(f'`{field.type_}` is too comple type for `{self.__class__.__name__}`')

        return self._create_type(field, parents, force_type=list[BaseModel], models=models, **kwargs) 

    def _create_enummeta(self, field, parents, **kwargs):
        return self._create_type(field, parents, force_type=Enum, **kwargs)

    def _create_type(self, field: ModelField, parents: Optional[Iterable[str]] = None, force_type: Optional[type] = None, **kwargs):
        logger.debug(f"[{self.__class__.__name__}][_create_type]: {field.name=}; {parents=};")

        view_cls = self.CONVERT_DIALECTS.get(force_type or field.type_)

        if view_cls is None:
            raise NotImplementedError(f'`{field.type_}` is not supported in {self.__class__.__name__}')

        return view_cls.create(field, parents=parents, **kwargs)

    def _create_modelmetaclass(self, field: ModelField, parents: Optional[Iterable[str]] = None, **kwargs):
        kwargs.pop('state')
        states = getattr(kwargs.pop('states'), field.name)
        logger.debug(f"[{self.__class__.__name__}][_create_modelmetaclass_view]: {field.name=}; {parents=}; {kwargs=};")
        parents = (*parents, field.name) if parents else (field.name,)
        return self.create_by_schema(field.type_, parents=parents, **kwargs, states=states) 

