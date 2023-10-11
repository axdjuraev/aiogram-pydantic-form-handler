from abc import abstractmethod
from typing import Any
from aiogram import Router

from aiogram.fsm.context import FSMContext
from ..types import TEvent, BaseSingleHandler


class AbstractController(BaseSingleHandler):
    @abstractmethod
    async def __call__(self, self_, event: TEvent, state: FSMContext) -> Any:
        raise NotImplementedError

    @abstractmethod
    def register2router(self, router: Router) -> Router:
        raise NotImplementedError

