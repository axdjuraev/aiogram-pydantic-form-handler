from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, Optional
from aiogram.fsm.state import StatesGroup
from axabc.logging import SimpleFileLogger
from pydantic.fields import ModelField


logger = SimpleFileLogger('aiogram-pydantic-handler')


class BaseFieldFactory(ABC):
    CONVERT_DIALECTS: dict[type, Any] = {}

    @abstractmethod
    def create(self, field: ModelField, states: StatesGroup, parents: Optional[Iterable[str]] = None, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def _create(self, field: ModelField, type_: type, states: StatesGroup, parents: Optional[Iterable[str]] = None, **kwargs):
        raise NotImplementedError

    def create4type(self, field: ModelField, parents: Optional[Iterable[str]] = None, force_type: Optional[type] = None, **kwargs):
        logger.debug(f"[{self.__class__.__name__}][_create_type]: {field.name=}; {parents=};")

        view_cls = self.CONVERT_DIALECTS.get(force_type or field.type_, self.CONVERT_DIALECTS.get(str))

        if view_cls is None:
            raise NotImplementedError(f'`{field.type_}` is not supported in {self.__class__.__name__}')

        return view_cls.create(field=field, parents=parents, **kwargs)

