from aiogram.types import InputMedia
from axabc.logging import SimpleStreamLogger
from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, Optional
from aiogram.fsm.state import StatesGroup
from pydantic.fields import ModelField

from pydantic_base_aiogram.types import FileType


logger = SimpleStreamLogger.create('aiogram-pydantic-handler')


class BaseFieldFactory(ABC):
    CONVERT_DIALECTS: dict[type, Any] = {}

    def __init__(self) -> None:
        self._unit_types = self._get_unit_types()

    def _get_unit_types(self) -> list:
        return [
            InputMedia,
            FileType,
        ]

    @abstractmethod
    def create(self, field: ModelField, states: StatesGroup, parents: Optional[Iterable[str]] = None, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def _create(self, field: ModelField, type_: type, states: StatesGroup, parents: Optional[Iterable[str]] = None, **kwargs):
        raise NotImplementedError

    def create4type(
        self, 
        field: ModelField, 
        parents: Optional[Iterable[str]] = None, 
        force_type: Optional[type] = None, 
        _except_steps: Optional[Iterable] = None,
        **kwargs
    ):
        logger.debug(f"[{self.__class__.__name__}][_create_type]: {field.name=}; {parents=};")

        view_cls = self.CONVERT_DIALECTS.get(force_type or field.type_, self.CONVERT_DIALECTS.get(str))

        if view_cls is None:
            raise NotImplementedError(f'`{field.type_}` is not supported in {self.__class__.__name__}')

        res = view_cls.create(field=field, parents=parents, **kwargs)

        if (
            hasattr(res, 'step_name') 
            and _except_steps 
            and getattr(res, 'step_name') in _except_steps
        ):
            return None

        return res

