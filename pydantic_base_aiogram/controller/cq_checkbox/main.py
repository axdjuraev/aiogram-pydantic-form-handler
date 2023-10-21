from pydantic_base_aiogram.field_factory import MultiSingeSplitter

from .single import SingleCQCheckboxController as Single
from .multiple import MultipleCQCheckboxController as Multiple


CQCheckboxController = MultiSingeSplitter(Single, Multiple)

