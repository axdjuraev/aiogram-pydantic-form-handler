from typing import Union
from typing import _GenericAlias, GenericAlias  # type: ignore
from pydantic.fields import ModelField
from pydantic_handler_converter.field_factory import logger

from .base import BaseEnumController as Base
from .single import SingleValueEnumController as Single
from .multiple import MultipleValueEnumController as Multiple


class EnumController(Base):
    @classmethod
    def create(cls, field: ModelField, **kwargs):
        logger.debug(f"[{cls.__name__}][create]: {field.name=};")
        if isinstance(field.outer_type_, Union[_GenericAlias, GenericAlias]):
            return Multiple.create(field, **kwargs)

        return Single(field=field, **kwargs)

