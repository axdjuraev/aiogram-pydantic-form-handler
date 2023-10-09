from abc import ABC
from typing import Iterable, Optional
from aiogram.fsm.state import StatesGroup
from pydantic.fields import ModelField

from .base import logger
from .base import BaseFieldFactory as Base
from .union import UnionFieldFactory as Union
from .model import ModelFieldFactory as Model


class FieldFactory(Model, Union, Base, ABC):
    def create(self, field: ModelField, states: StatesGroup, parents: Optional[Iterable[str]] = None, **kwargs):
        type_ = field.type_
        base_type_name = str(type(type_).__name__).lower()
        logger.debug(f"[{self.__class__.__name__}][create]: {field.name=}; {type_=}; {base_type_name=}")

        try: 
            creator = getattr(self, f'create4{base_type_name}')
        except AttributeError as e:
            logger.error(str(e))
            raise NotImplementedError(f'`{base_type_name}` is not supported metatype in {self.__class__.__name__}')

        state = getattr(states, field.name)
        res = creator(field, state=state, states=states, **kwargs, parents=parents)
        return res

