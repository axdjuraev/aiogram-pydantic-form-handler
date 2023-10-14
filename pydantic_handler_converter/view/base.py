from abc import abstractmethod
from typing import Any, Iterable, Optional, Union
from typing import _GenericAlias, GenericAlias  # type: ignore
from pydantic.fields import ModelField
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State

from pydantic_handler_converter.types import Event
from pydantic_handler_converter.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_handler_converter.dialecsts import BaseDialects
from pydantic_handler_converter.field_factory import logger
from .abstract import AbstractView


class BaseView(AbstractView):
    def __init__(
        self, 
        field: ModelField, 
        state: State,
        dialects: BaseDialects, 
        parents: Iterable[str],
        filters: Iterable = tuple(),
        is_has_back: Optional[str] = None,
        tree_id: Optional[int] = None,
        **_,
    ) -> None:
        self.field = field
        self.state = state
        self.dialects = dialects
        self.parents = parents
        self.filters = filters
        self.is_has_back = is_has_back
        self.step_name = self._get_step_name()
        self.name = self._get_name()
        self.callback_data = self._get_callback_data()
        self.keyboard = self._get_keyboard()
        self.tree_id = tree_id
        super().__init__()
        logger.debug(f"[{self.__class__.__name__}][__init__]: {locals()=};")

    def _get_keyboard(self, builder: Optional[InlineKeyboardBuilder] = None):
        builder = builder or InlineKeyboardBuilder()

        if not self.field.required:
            builder.button(
                text=self.dialects.SKIP_BUTTON,
                callback_data=self.dialects.SKIP_STEP_DATA,
            )

        logger.debug(f"[{self.__class__.__name__}][_get_keyboard]: {self.is_has_back=}; {locals()=};")
        if self.is_has_back:
            builder.button(
                text=self.dialects.BACK_BUTTON, 
                callback_data=self.dialects.BACK_BUTTON_DATA,
            )

        if isinstance(self.field.outer_type_, Union[_GenericAlias, GenericAlias]):
            builder.button(
                text=self.dialects.READY_BUTTON, 
                callback_data=self.dialects.READY_BUTTON_DATA, 
            )

        return builder.adjust(1)

    def _get_step_name(self) -> str:
        if len(tuple(self.parents)) < 2:
            return f"{self.field.name}"

        return f'{"".join(tuple(self.parents)[1:])}_{self.field.name}'

    def _get_name(self) -> str:
        return f"{self.step_name}_view"

    def _get_callback_data(self) -> str:
        top_levels = '.'.join(self.parents or tuple())
        return f"{top_levels}.{self.field.name}"

    def register2router(self, router: Router) -> Router:
        router.callback_query(F.data.startswith(self.callback_data), *self.filters)(self.__call__)

        logger.debug(f"[{self.__class__.__name__}][register2router]: {locals()=};")
        return router

    async def __call__(self, self_: THandler, event, state: FSMContext) -> Any:
        event = Event(event)
        res = await self.main(self_, event, state)
        await self._set_current_step(state)
        return res

    async def _set_current_step(self, state: FSMContext):
        await state.update_data(__step__=self.step_name)

    @abstractmethod
    async def main(self, self_: THandler, event: Event, state: FSMContext) -> Any:
        raise NotImplementedError

    @classmethod
    def create(cls, field: ModelField, **kwargs) -> 'BaseView':
        logger.debug(f"[{cls.__name__}][create]: {field.name=};")
        return cls(field=field, **kwargs)

