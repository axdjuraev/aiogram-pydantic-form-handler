from abc import abstractmethod
from enum import Enum
from itertools import chain
from typing import Callable, Type, Union
from pydantic import BaseModel
from pydantic.fields import ModelField
from pydantic_base_aiogram.utils.abstractions import is_list_type
from pydantic_base_aiogram.utils.step import get_step_name
from .base import BaseFieldFactory, logger


class UnionFieldFactory(BaseFieldFactory):
    create_by_schema: Callable 
    
    def _countup_things(self, field, things: list):
        strs_count = 0
        enums = []
        models = []

        for item in things:
            if issubclass(item, Enum):
                enums.append(item)
            elif issubclass(item, BaseModel):
                models.append(item)
            elif issubclass(item, Union[str, float, int]):
                strs_count += 1
            else:
                raise NotImplementedError(f'`{field.type_}` is too comple type for `{self.__class__.__name__}`')

        return strs_count, enums, models

    @abstractmethod
    def create4models(self, field: ModelField, models: list[Type[BaseModel]], kwargs: dict):
        elems = []
        models_dialects = {}
        tree_head_step_name = get_step_name(field, kwargs['parents'])

        for tree_id, model in enumerate(models, start=1):
            logger.debug(f"[{self.__class__.__name__}][create4models]: {locals()=}")
            model_views = self.create_by_schema(
                model, 
                tree_id=tree_id, 
                tree_head_step_name=tree_head_step_name, 
                is_list_item=is_list_type(field.outer_type_),
                **kwargs,
            )

            if model_views:
                models_dialects[model] = model_views[0]
                elems.extend(model_views)

        return elems, models_dialects

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

        kwargs['parents'] = (*parents, field.name)
        kwargs['states'] = getattr(kwargs['states'], field.name)
        
        return self.create4models(field, models=models, kwargs=kwargs) 

