from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Iterable, Optional, Union
from pydantic.fields import ModelField
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.filters.state import StateFilter

from pydantic_base_aiogram.abstract_handler import AbstractPydanticFormHandlers as THandler
from pydantic_base_aiogram.field_factory import logger
from pydantic_base_aiogram.types import Event
from pydantic_base_aiogram.exceptions import DataValidationError, RequireMultipleError
from pydantic_base_aiogram.utils.abstractions import is_list_type

from .abstract import AbstractController


class BaseController(AbstractController, ABC):
    def __init__(
        self, 
        state: State,
        filters: Iterable = tuple(),
        async_data_validator: Optional[Callable[[Event, FSMContext], Awaitable[Any]]] = None,
        data_validator: Optional[Callable[[Event, FSMContext], Any]] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs, name_format="{step_name}_ctrl")
        self.item_callback_data = "ielem"
        self.state = state
        self.filters = filters
        self.callback_data = self._get_callback_data()
        self._async_data_validator = async_data_validator or self.field.field_info.extra.get('async_data_validator')
        self._data_validator = data_validator or self.field.field_info.extra.get('data_validator')
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

        if not is_list_type(self.field.outer_type_):
            parent_elem[self.field.name] = value
        else:
            elems = parent_elem.get(self.field.name, [])

            if isinstance(value, Iterable):
                elems.extend(value)
            else:
                elems.append(value)

            parent_elem[self.field.name] = elems

        await state.update_data(**data)

    async def __call__(self, self_: THandler, event: Union[types.Message, types.CallbackQuery], state: FSMContext) -> Any:
        return await self.main(self_, Event(event), state)  # type: ignore

    @abstractmethod
    async def format_data(self, self_: THandler, event: Event, state: FSMContext):
        raise NotImplementedError
    
    async def validate_data_format(self, self_, event, state):
        if self._async_data_validator:
            return await self._async_data_validator(event, state)
        if self._data_validator:
            return self._data_validator(event, state)

        return await self.format_data(self_, event, state)

    async def main(self, self_: THandler, event: Event, state: FSMContext) -> Any:
        try:
            res = await self.validate_data_format(self_, event, state)
        except ValueError:
            return await event.answer(self.dialects.INVALID_TYPE_DATA)
        except DataValidationError as e:
            return await event.answer(e.detail)
        except RequireMultipleError as e:
            return await self._setvalue(e.value, state)

        if res is ...:
            return

        await self._setvalue(res, state)
        await self_.next(event, state, self.step_name)

    def register2router(self, router: Router) -> Router:
        router.message(StateFilter(self.state))(self.__call__)
        
        logger.debug(f"[{self.__class__.__name__}][register2router]: {locals()=};")
        return router

    @classmethod
    def create(cls, field: ModelField, **kwargs) -> 'BaseController':
        logger.debug(f"[{cls.__name__}][create]: {field.name=};")
        return cls(field=field, **kwargs)

