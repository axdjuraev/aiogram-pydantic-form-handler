from typing import Callable, Iterable, Optional, Union
from pydantic import BaseModel
from pydantic_base_aiogram.exceptions import TypeFactoryNotFound
from pydantic_base_aiogram.types import BaseFactory, BaseFieldFactory

from pydantic_base_aiogram.utils.field_normalization import extra 
from pydantic_base_aiogram.utils.field_normalization import TypeNormilizer
from pydantic_base_aiogram.utils.field_normalization.extra import normilize_dialect_keys
from pydantic_base_aiogram.utils.field_normalization.normilized_model_field import NormalizedModelField


class FieldFactory(BaseFieldFactory):
    @property
    def factory_dialects(self) -> dict[
        Union[type, Iterable[type]], 
        Union[type[BaseFactory], Callable[[NormalizedModelField], list]],
    ]:
        return {
            BaseModel: self._create_for_schema,
            (BaseModel,): self._create_for_union_schema,
        }

    def __init__(self) -> None:
        self._type_normalizer = TypeNormilizer()
        (
            self.factory_dialects,  # type: ignore 
            self.available_unique_types,
        ) = normilize_dialect_keys(self.factory_dialects)

    def _create_for_union_schema(self, field: NormalizedModelField, items: Optional[list] = None, **kwargs) -> list:
        items = items or []

        for tree_id, schema in enumerate(field._types, start=0):
            items.extend(self.create_by_schema(schema, tree_id=tree_id, **kwargs))

        return items

    def _create_for_schema(self, field: NormalizedModelField, **kwargs) -> list:
        return self.create_by_schema(field.field_type, **kwargs)  # type: ignore

    def create_by_schema(
        self, 
        schema: type[BaseModel], 
        items: Optional[list] = None, 
        tree_head_step_name: Optional[str] = None,
        parents: Optional[tuple[str]] = None,
        **kwargs,
    ) -> list:
        items = items or []
        parents = parents or (schema.__name__,)

        for field in schema.__fields__.values():
            field_type = field.field_info.extra.get('force_type') or field.type_
            types, is_list = self._type_normalizer.normalize_type(field_type)
            types = tuple(types)
            search_key: tuple[type] = extra.mro_base_search(types, self.available_unique_types)  # type: ignore

            if items and not tree_head_step_name:
                tree_head_step_name = items[-1].step_name

            if None in search_key:
                raise TypeFactoryNotFound(f'Factory not found for `{field_type}`')

            search_key = tuple(sorted(set(search_key), key=lambda x: x.__name__))
            factory = self._get_factory(search_key)

            field_ = NormalizedModelField(
                field=field,
                field_type=field_type,
                types=types,
                mro_search_key=search_key,
                is_list=is_list,
            )

            kwargs = {
                **field.field_info.extra, 
                'items': items,
                'tree_head_step_name': tree_head_step_name,
                **kwargs,
            }

            items.extend(factory(field_, **kwargs))

        return items

    def _get_factory(self, t: tuple[type]) -> Callable:
        if not (factory := self.factory_dialects.get(t)):
            raise TypeFactoryNotFound(f'Factory not found for types `{t}`')
        
        if isinstance(factory, Callable):
            return factory
        
        return factory.create

