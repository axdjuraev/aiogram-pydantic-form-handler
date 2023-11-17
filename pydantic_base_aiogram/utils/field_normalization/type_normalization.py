from types import UnionType
from typing import Union, Optional, get_origin, get_args
from pydantic_base_aiogram.exceptions import TooNestedType


class TypeNormilizer:
    TUnions = (Union, UnionType)

    def _decompose_union(self, type_: type) -> Optional[tuple[type]]:
        if get_origin(type_) in self.TUnions:
            return get_args(type_)

        return None

    def _decompose_list(self, type_: type) -> tuple[type, bool]:
        is_list = False
        
        if get_origin(type_) is list:
            is_list = True
            type_ = get_args(type_)[-1]

        return (type_, is_list)

    def normalize_type(self, type_: type) -> tuple[list[type], bool]:
        types = [type_]
        type_, is_list = self._decompose_list(type_) 
        union_types = self._decompose_union(type_)

        if union_types:
            is_lists = None
            types = [None for _ in range(len(union_types))]

            for idx in range(len(union_types)):
                t = union_types[idx]

                inner_type, is_item_list = self._decompose_list(t) 

                if not is_lists:
                    is_lists = is_item_list
                elif is_lists != is_item_list:
                    raise TooNestedType

                types[idx] = inner_type

            is_list = is_list or bool(is_lists)

        return (types, is_list)

