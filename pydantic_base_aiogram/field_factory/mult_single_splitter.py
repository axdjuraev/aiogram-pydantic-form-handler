from pydantic.fields import ModelField
from pydantic_base_aiogram.utils.abstractions import is_list_type
from .base import logger


class MultiSingeSplitter:
    def __init__(self, single_cls, multiple_cls) -> None:
        self.single_cls = single_cls
        self.multiple_cls = multiple_cls

    def create(self, field: ModelField, **kwargs):
        logger.debug(f"[{self.__class__.__name__}][create]: {field.name=};")
        if is_list_type(field.outer_type_):
            return self.multiple_cls.create(field=field, **kwargs)

        return self.single_cls.create(field=field, **kwargs)
