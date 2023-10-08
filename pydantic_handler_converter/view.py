from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional, Type
from pydantic.fields import ModelField
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State
from enum import Enum

from .abstract_handler import AbstractPydanticFormHandlers as THandler
from .abstract_view import AbstractView
from .base_field_factory import BaseFieldFactory, logger
from .dialecsts import BaseDialects
from .types import Event, DescriptiveEnum




class BaseView(AbstractView):
    def __init__(
        self, 
        field: ModelField, 
        state: State,
        dialects: BaseDialects, 
        parents: Iterable[str],
        filters: Iterable = tuple(),
        back_data: Optional[str] = None,
    ) -> None:
        self.field = field
        self.state = state
        self.dialects = dialects
        self.parents = parents
        self.filters = filters
        self.back_data = back_data
        self.name = self._get_name()
        self.callback_data = self._get_callback_data()
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

    def _get_name(self) -> str:
        return f'{"".join(tuple(self.parents)[1:])}_{self.field.name}_view'

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
        await event.answer(f"{self.dialects.INPUT_STR} {self.field.name}", reply_markup=self.keyboard)
        await state.set_state(self.state)


class FloatView(BaseView):
    async def main(self, _: THandler, event: Event, state: FSMContext) -> Any:
        await event.answer(f"{self.dialects.INPUT_STR} {self.field.name}", reply_markup=self.keyboard)
        await state.set_state(self.state)


class IntView(BaseView):
    async def main(self, _: THandler, event: Event, state: FSMContext) -> Any:
        await event.answer(f"{self.dialects.INPUT_INT} {self.field.name}", reply_markup=self.keyboard)
        await state.set_state(self.state)


class EnumView(BaseView):
    def __init__(self, field: ModelField, *args, **kwargs) -> None:
        super().__init__(field, *args, **kwargs)
        self.item_callback_data = f"elem_{self.callback_data}"

    def _enum2dict(self, enum: Type[Enum]) -> dict:
        res = {}
        for item in enum._member_map_.values():
            res[item.name] = (
                item.value if not isinstance(item, DescriptiveEnum) 
                else item.description
            )

        return res

    def _get_keyboard(self, builder: Optional[InlineKeyboardBuilder] = None):
        builder = builder or InlineKeyboardBuilder()

        for name, description in self._enum2dict(self.field.type_):
            builder.button(text=description, data=f"{self.item_callback_data}:{name}")

        return self._get_keyboard(builder)

    async def main(self, _: THandler, event: Event, state: FSMContext) -> Any:
        await event.answer(f"{self.dialects.CHOOSE_FROM_ENUM} {self.field.name}", reply_markup=self.keyboard)
        await state.set_state(self.state)


class ViewFactory(BaseFieldFactory, ABC):
    CONVERT_DIALECTS = {
        str: StrView,
        int: IntView,
        float: FloatView,
        Enum: EnumView,
    }

    def create(self, field: ModelField, parents: Optional[Iterable[str]] = None, **kwargs) -> Iterable[BaseView]:
        return super().create(field, parents, **kwargs)

