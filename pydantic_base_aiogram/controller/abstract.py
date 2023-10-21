from abc import abstractmethod
from types import MethodType
from typing import Any
from aiogram import Router
from aiogram.fsm.context import FSMContext

from pydantic_base_aiogram.field_factory import logger
from ..types import TEvent, BaseSingleHandler


class AbstractController(BaseSingleHandler):
    def bind(self, elem):
        self.__call__ = MethodType(self.__call__, elem)
        logger.debug(f"[{self.__class__.__name__}][{self.name}][bind]: {locals()=};")

        return self

    @abstractmethod
    async def __call__(self, self_, event: TEvent, state: FSMContext) -> Any:
        raise NotImplementedError

    @abstractmethod
    def register2router(self, router: Router) -> Router:
        raise NotImplementedError

