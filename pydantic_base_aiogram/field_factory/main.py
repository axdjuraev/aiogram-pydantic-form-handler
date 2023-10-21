from abc import ABC
from typing import Iterable, Optional
from aiogram.fsm.state import StatesGroup
from pydantic.fields import ModelField
from copy import deepcopy

from .base import logger
from .base import BaseFieldFactory as Base
from .enum import EnumFieldFactory as Enum
from .union import UnionFieldFactory as Union
from .model import ModelFieldFactory as Model


class FieldFactory(Model, Enum, Union, Base, ABC):
    def create(self, field: ModelField, states: StatesGroup, parents: Optional[Iterable[str]] = None, **kwargs):
        type_ = field.type_
        return self._create(field, type_, states, parents, **kwargs)
    
    def _create(self, field: ModelField, type_: type, states: StatesGroup, parents: Optional[Iterable[str]] = None, **kwargs):
        if type_ != field.type_:
            field = deepcopy(field)
            field.type_ = type_

        base_type_name = str(type(type_).__name__).lower()
        logger.debug(f"[{self.__class__.__name__}][create]: {field.name=}; {type_=}; {base_type_name=}")

        try: 
            creator = getattr(self, f'create4{base_type_name}', self.create4type)
        except AttributeError as e:
            logger.error(str(e))
            raise NotImplementedError(f'`{base_type_name}` is not supported metatype in {self.__class__.__name__}')

        logger.debug(f"[{self.__class__.__name__}][create]: {dir(states)=}")
        state = getattr(states, field.name)
        kwargs['state'] = state
        res = creator(field, states=states, **kwargs, parents=parents)
        return res

