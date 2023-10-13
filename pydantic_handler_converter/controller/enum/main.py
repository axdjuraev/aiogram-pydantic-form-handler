from pydantic_handler_converter.field_factory import MultiSingeSplitter

from .single import SingleValueEnumController as Single
from .multiple import MultipleValueEnumController as Multiple


EnumController = MultiSingeSplitter(Single, Multiple)

