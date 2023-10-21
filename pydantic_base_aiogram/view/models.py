from types import MethodType
from typing import Type
from uuid import uuid4
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from pydantic import BaseModel

from pydantic_base_aiogram.abstract_handler import (
    AbstractPydanticFormHandlers as THandler 
)
from pydantic_base_aiogram.types import DescriptiveSchema
from .base import BaseView


class ModelsView(BaseView):
    DATA_SPLIT_SYMBOL = ':'

    def __init__(self, *args, models_dialects: dict[Type[BaseModel], BaseView], **kwargs) -> None:
        self.models_dialects = models_dialects
        self.model_list_dialects = tuple(self.models_dialects.values())
        super().__init__(*args, item_callback_data=str(uuid4()), **kwargs)

    @property
    def view_text_format(self):
        return self.dialects.CHOOSE_FIELD_TYPE

    @property
    def extra_keys(self) -> dict[str, str]:
        keys = super().extra_keys

        for index, model in enumerate(self.models_dialects.keys()):
            model_cls_name = model.__name__
            model_name = model_cls_name

            if isinstance(model, DescriptiveSchema):
                model_name = model.__NAME__

            keys[f"{self.item_callback_data}{self.DATA_SPLIT_SYMBOL}{index}"] = model_name

        return keys

    async def _save_tree_choice(self, state: FSMContext, tree_index: int):
        await state.update_data({f'__tree_choice_{self.step_name}__': tree_index})

    async def item_select_handler(self, _: THandler, event: CallbackQuery, state: FSMContext):
        index = int(str(event.data).split(self.DATA_SPLIT_SYMBOL)[1])
        res = await self.model_list_dialects[index].__call__(event, state)  # type: ignore
        await self._save_tree_choice(state, index)
        return res

    def bind(self, elem):
        self.item_select_handler = MethodType(self.item_select_handler, elem)
        return super().bind(elem)

    def register2router(self, router: Router) -> Router:
        router.callback_query(F.data.startswith(self.item_callback_data))(self.item_select_handler)
        return super().register2router(router)

