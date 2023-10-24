from typing import get_origin


def is_list_type(obj):
    type = obj

    if (type_ := get_origin(obj)):
        type = type_
        
    return issubclass(type, list)

