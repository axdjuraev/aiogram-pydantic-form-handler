from enum import Enum
from itertools import chain
from typing import Union
from pydantic import BaseModel
from pydantic.fields import ModelField
from .base import BaseFieldFactory


class UnionFieldFactory(BaseFieldFactory):
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

    def create4uniontype(self, field: ModelField, parents, **kwargs):
        return self.create4_uniongenericalias(field, parents, **kwargs)

    def create4_uniongenericalias(self, field: ModelField, parents, **kwargs):
        args = field.type_.__args__
        all_count = len(args)
        strs_count, enums, models = self._countup_things(field, args)

        if strs_count == all_count:
            return self.create4type(field, parents, force_type=str, **kwargs)

        if all_count == (len(enums) + strs_count):
            combined_name = ''.join(map(lambda x: x.__name__, enums))
            type_ = Enum(combined_name, [(x.name, x.value) for x in chain(*enums)])
            return self._create(field, type_=type_, parents=parents, is_string_allowed=strs_count > 0, **kwargs)

        elif strs_count or len(enums):
            raise NotImplementedError(f'`{field.type_}` is too comple type for `{self.__class__.__name__}`')

        return self.create4type(field, parents, force_type=list[BaseModel], models=models, **kwargs) 

