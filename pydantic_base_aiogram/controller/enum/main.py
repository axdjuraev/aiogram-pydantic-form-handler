from pydantic_base_aiogram.field_factory import MultiSingeSplitter

from .single import SingleValueEnumController as Single
from .multiple import MultipleValueEnumController as Multiple


EnumController = MultiSingeSplitter(Single, Multiple)

