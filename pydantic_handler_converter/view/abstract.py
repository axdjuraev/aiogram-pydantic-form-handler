from abc import ABC, abstractmethod
from typing import Any
from aiogram import Router

from aiogram.fsm.context import FSMContext
from ..types import TEvent


class AbstractView(ABC):
    @abstractmethod
    async def __call__(self, self_, event: TEvent, state: FSMContext) -> Any:
        raise NotImplementedError

    @abstractmethod
    def register2router(self, router: Router) -> Router:
        raise NotImplementedError

