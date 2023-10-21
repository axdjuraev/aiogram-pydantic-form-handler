from pydantic_base_aiogram.field_factory import MultiSingeSplitter

from .single import SingleValueCustomDataController as Single
from .multiple import MultipleValueCustomDataController as Multiple


CustomDataStrController = MultiSingeSplitter(Single, Multiple)

