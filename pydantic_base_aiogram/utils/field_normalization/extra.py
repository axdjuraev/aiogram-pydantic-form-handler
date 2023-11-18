from typing import Iterable, Union, Callable, Optional
from functools import lru_cache


TDialect = dict[
    Union[type, Iterable[type]], 
    Union[type[object], Callable],
]
TNormilizedDialect = dict[
    tuple[type], 
    Union[type[object], Callable],
]
TMROSearchResult = tuple[list[type], list[type]]


def normilize_dialect_keys(dialect: TDialect) -> tuple[TNormilizedDialect, tuple[type]]:
    normilized = {}
    available_unique_types = []

    for k, v in dialect.items():
        if not isinstance(k, Iterable):
            k = (k,)
        else:
            k = tuple(sorted(set(k), key=lambda x: x.__name__))

        normilized[k] = v

        for t in k:
            if not t in available_unique_types:
                available_unique_types.append(t)

    return normilized, tuple(available_unique_types)
  

@lru_cache()
def _mro_base_search(t: type, available_unique_types) -> Optional[type]:
    if not len(t.__bases__) > 1:
        return None

    if t in available_unique_types:
        return t

    for base in t.__bases__:
        if base is object:
           continue 

        if base in available_unique_types:
            return base

    return None
  

@lru_cache()
def mro_base_search(
    types: Iterable[type], 
    available_unique_types: tuple,
) -> list[Optional[type]]:
    result = []
 
    for t in types:
        base = _mro_base_search(t, available_unique_types)
        result.append(base)

    return result

