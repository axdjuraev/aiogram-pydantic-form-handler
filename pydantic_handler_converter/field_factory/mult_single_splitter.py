from typing import Union
from typing import _GenericAlias, GenericAlias  # type: ignore
from pydantic.fields import ModelField
from .base import logger


class MultiSingeSplitter:
    def __init__(self, single_cls, multiple_cls) -> None:
        self.single_cls = single_cls
        self.multiple_cls = multiple_cls

    def create(self, field: ModelField, **kwargs):
        logger.debug(f"[{self.__class__.__name__}][create]: {field.name=};")
        if isinstance(field.outer_type_, Union[_GenericAlias, GenericAlias]):
            return self.multiple_cls.create(field, **kwargs)

        return self.single_cls.create(field=field, **kwargs)
