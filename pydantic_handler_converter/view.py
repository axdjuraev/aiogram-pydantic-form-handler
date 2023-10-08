from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional
from pydantic.fields import ModelField
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State

from .abstract_handler import AbstractPydanticFormHandlers as THandler
from .base_field_factory import BaseFieldFactory, logger
from .dialecsts import BaseDialects
from .event import Event


class ViewFactory(BaseFieldFactory, ABC, elem_postfix='View'):
    pass


class BaseView(ABC):
    def __init__(
        self, 
        field: ModelField, 
        state: State,
        dialects: BaseDialects, 
        filters: Iterable = tuple(),
        back_data: Optional[str] = None,
        parents: Optional[Iterable[str]] = None,
    ) -> None:
        self.field = field
        self.state = state
        self.dialects = dialects
        self.parents = parents
        self.callback_data = self._get_callback_data()
        self.filters = filters
        self.back_data = back_data
        self.keyboard = self._get_keyboard()

    def _get_keyboard(self, builder: Optional[InlineKeyboardBuilder] = None):
        builder = builder or InlineKeyboardBuilder()

        if not self.field.required:
            builder.button(
                text=self.dialects.SKIP_BUTTON,
                callback_data=self.dialects.SKIP_STEP_DATA,
            )

        if self.back_data:
            builder.button(
                text=self.dialects.BACK_BUTTON, 
                callback_data=self.back_data
            )

        return builder.adjust(1)

    def _get_callback_data(self) -> str:
        top_levels = '.'.join(self.parents or tuple())
        return f"{top_levels}.{self.field.name}"

    def register2router(self, router: Router) -> Router:
        router.callback_query(F.data.startswith(self.callback_data), *self.filters)(self.__call__)

        return router

    async def __call__(self, self_: THandler, event, state: FSMContext) -> Any:
        event = Event(event)
        return await self.main(self_, event, state)

    @abstractmethod
    async def main(self, self_: THandler, event: Event, state: FSMContext) -> Any:
        raise NotImplementedError

    @classmethod
    def create(cls, field: ModelField, **kwargs) -> 'BaseView':
        logger.debug(f"[{cls.__name__}][create]: {field.name=};")
        return cls(field=field, **kwargs)


class StrView(BaseView):
    async def main(self, _: THandler, event: Event, state: FSMContext) -> Any:
        await event.answer(f"{self.dialects.INPUT_STR} {self.field.name}")
        await state.set_state(self.state)


class FloatView(BaseView):
    async def main(self, _: THandler, event: Event, state: FSMContext) -> Any:
        await event.answer(f"{self.dialects.INPUT_STR} {self.field.name}")
        await state.set_state(self.state)


class IntView(BaseView):
    async def main(self, _: THandler, event: Event, state: FSMContext) -> Any:
        await event.answer(f"{self.dialects.INPUT_INT} {self.field.name}")
        await state.set_state(self.state)


class EnumView(BaseView):
    def _enum2dict() -> dict:
        pass

    def _get_keyboard(self, builder: Optional[InlineKeyboardBuilder] = None):
        builder = builder or InlineKeyboardBuilder()
        return self._get_keyboard(builder)

    async def main(self, _: THandler, event: Event, state: FSMContext) -> Any:
        await event.answer(f"{self.dialects.CHOOSE_FROM_ENUM} {self.field.name}")
        await state.set_state(self.state)

