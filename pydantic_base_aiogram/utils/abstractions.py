from typing import get_args, get_origin, Union
from inspect import isclass


def is_list_type(obj):
    obj_type = obj

    if (type_ := get_origin(obj)):
        if type_ is not Union:
            obj_type = type_
        elif (type_ := get_origin((args := get_args(obj)) and args[0])):
            obj_type = type_
        
    return isclass(obj_type) and issubclass(obj_type, list)

