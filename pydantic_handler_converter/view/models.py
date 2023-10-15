from types import MethodType
from typing import Optional, Type
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pydantic import BaseModel

from pydantic_handler_converter.abstract_handler import (
    AbstractPydanticFormHandlers as THandler 
)
from pydantic_handler_converter.types import Event
from .base import BaseView


class ModelsView(BaseView):
    def __init__(self, *args, models_dialects: dict[Type[BaseModel], BaseView], **kwargs) -> None:
        self.models_dialects = models_dialects
        self.model_list_dialects = tuple(self.models_dialects.values())
        self.item_callback_data = None 
        super().__init__(*args, **kwargs)

    def _get_keyboard(self, builder: Optional[InlineKeyboardBuilder] = None):
        if self.item_callback_data is None:
            self.item_callback_data = f"item_{self.callback_data}"

        builder = builder or InlineKeyboardBuilder()

        for index, model in enumerate(self.models_dialects.keys()):
            model_cls_name = model.__name__

            try:
                model_name = getattr(model, 'name')
            except AttributeError:
                model_name = model_cls_name

            builder.button(
                text=model_name,
                callback_data=f"{self.item_callback_data}:{index}"
            )

        return super()._get_keyboard(builder) 


    async def _save_tree_choice(self, state: FSMContext):
        await state.update_data(__tree_choice__)

    async def item_select_handler(self, self_: THandler, event: CallbackQuery, state: FSMContext):
        _, index = str(event.data).split(':')
        await self.model_list_dialects[int(index)].__call__(event, state)  # type: ignore

    async def main(self, self_: THandler, event: Event, _: FSMContext):
        await event.answer(self.dialects.CHOOSE_FIELD_TYPE, reply_markup=self.keyboard.as_markup())

    def bind(self, elem):
        self.item_select_handler = MethodType(self.item_select_handler, elem)
        return super().bind(elem)

    def register2router(self, router: Router) -> Router:
        router.callback_query(F.data.startswith(self.item_callback_data), *self.filters)(self.item_select_handler)
        return super().register2router(router)

