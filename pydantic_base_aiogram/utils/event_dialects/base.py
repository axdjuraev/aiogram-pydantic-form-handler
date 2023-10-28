from abc import ABC, abstractmethod

from aiogram.fsm.context import FSMContext


class BaseEventDialect(ABC):
    @abstractmethod
    @staticmethod
    async def answer(event, text, state: FSMContext, **_):
        pass

