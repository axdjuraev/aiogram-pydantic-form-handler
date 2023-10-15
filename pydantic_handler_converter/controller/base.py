from typing import Any, Iterable, Union
from typing import _GenericAlias, GenericAlias  # type: ignore
from pydantic.fields import ModelField
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.filters.state import StateFilter

from pydantic_handler_converter.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_handler_converter.field_factory import logger
from pydantic_handler_converter.types import Event

from .abstract import AbstractController


class BaseController(AbstractController):
    def __init__(
        self, 
        state: State,
        filters: Iterable = tuple(),
        **kwargs,
    ) -> None:
        super().__init__(**kwargs, name_format="{step_name}_ctrl")
        self.state = state
        self.filters = filters
        self.callback_data = self._get_callback_data()
        logger.debug(f"[{self.__class__.__name__}][__init__]: {locals()=};")

    def _get_callback_data(self) -> str:
        top_levels = '.'.join(self.parents or tuple())
        return f"{top_levels}.{self.field.name}"

    async def _setvalue(self, value, state: FSMContext):
        data = await state.get_data()
        parent_elem = data

        for parent_name in self.parents:
            parent = parent_elem.get(parent_name)

            if parent is None:
                parent = {}
                parent_elem[parent_name] = parent

            parent_elem = parent

        if not isinstance(self.field.outer_type_, Union[_GenericAlias, GenericAlias]):
            parent_elem[self.field.name] = value
        else:
            elems = parent_elem.get(self.field.name, [])

            if isinstance(value, Iterable):
                elems.extend(value)
            else:
                elems.append(value)

            parent_elem[self.field.name] = elems

        await state.update_data(**data)

    async def __call__(self, self_: THandler, event: types.Message, state: FSMContext) -> Any:
        if not event.text:
            return await event.delete()

        return await self.main(self_, event, state)

    async def main(self, self_: THandler, event: types.Message, state: FSMContext) -> Any:
        try:
            res = self.field.type_(event.text)
        except ValueError:
            return await event.delete()
        await self._setvalue(res, state)
        await self_.next(Event(event), state, self.step_name)  # type: ignore

    def register2router(self, router: Router) -> Router:
        router.message(StateFilter(self.state))(self.__call__)
        
        logger.debug(f"[{self.__class__.__name__}][register2router]: {locals()=};")
        return router

    @classmethod
    def create(cls, field: ModelField, **kwargs) -> 'BaseController':
        logger.debug(f"[{cls.__name__}][create]: {field.name=};")
        return cls(field=field, **kwargs)

