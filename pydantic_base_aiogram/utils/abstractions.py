from typing import get_origin
from inspect import isclass


def is_list_type(obj):
    type = obj

    if (type_ := get_origin(obj)):
        type = type_
        
    return isclass(obj) and issubclass(type, list)

