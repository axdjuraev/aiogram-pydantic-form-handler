from typing import TypeVar
from pydantic import BaseModel, Field
from pydantic_base_aiogram.abstract_handler import AbstractPydanticFormHandlers


BaseType = TypeVar('BaseType', bound=AbstractPydanticFormHandlers)


def create_add_more_handlers(self: BaseType) -> BaseType:
    class AddMoreSchema(BaseModel):
        add_more: bool = Field(
            view_text=self.DIALECTS.ADD_MORE, 
            extra_keys={
                self.DIALECTS.BACK_BUTTON_DATA: self.DIALECTS.BACK_BUTTON,
            }
        )

    async def final_call(data: AddMoreSchema, event, state):
        if data.add_more:
            return await self.next(event, state, restart_loop=True)
        
        return await self.next(event, state, skip_loop_prompt=True)

    return type(
        'AddMoreHandlers', 
        (self.__class__,), 
        {
            '__full_load__': False,
        }
    )(finish_call=final_call)  # type: ignore

