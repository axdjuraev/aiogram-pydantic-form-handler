from abc import ABC
from typing import Iterable, Optional, Type, Union
from datetime import date
from pydantic import BaseModel
from pydantic.fields import ModelField
from enum import Enum
from aiogram.types import InputMedia

from pydantic_base_aiogram.field_factory import FieldFactory

from .type_base_message_text import TypeBaseMessageTextController
from .date_message_text import DateMessageTextController
from .cq_checkbox import CQCheckboxController
from .custom_data_str import CustomDataStrController
from .bool import BoolController
from .file import FileController


class ControllerFactory(FieldFactory, ABC):
    CONVERT_DIALECTS = {
        str: TypeBaseMessageTextController,
        Enum: CQCheckboxController,
        Union[str, Enum]: CustomDataStrController,
        bool: BoolController,
        date: DateMessageTextController,
    }

    def create4models(self, field: ModelField, models: list[Type[BaseModel]], kwargs: dict):
        res, _ = super().create4models(field, models, kwargs)
        return res

    def create4type(self, field: ModelField, parents: Optional[Iterable[str]] = None, force_type: Optional[type] = None, **kwargs):
        if field.field_info.extra.get('getter'):
            force_type = Union[str, Enum]

        return super().create4type(field, parents, force_type, **kwargs)

