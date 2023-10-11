```python
#-------------------configuration-settings-schema-declaration--------------------
>>> from pydantic import BaseSettings
>>>
>>>
>>> class Settings(BaseSettings):
...     BOT_TOKEN: str
... 
...     class Config:
...         env_file = '.env'
... 
... 
#---------------------------priority-enum-declaration----------------------------
>>> from enum import Enum
>>>
>>>
>>> class PriorityEnum(Enum):
...     LOW = "low", "not really serios"
...     MEDIUM = "medium", "it's not urgent, but it's best to see if possible."
...     HIGH = "high", "it's very important"
... 
...     def __init__(self, name, description) -> None:
...         self._name = name
...         self._description = description
... 
...     @property
...     def name(self) -> str:
...         return super().name
...     
...     @property
...     def description(self) -> str:
...         return self._description
... 
... 
#---------------------------actual-schema-declaration----------------------------
>>> from pydantic import BaseModel
>>>
>>>
>>> class TicketSchema(BaseModel):
...     title: str
...     short_description: str
...     priority: PriorityEnum
... 
... 
#--------------------------------using-converter---------------------------------
>>> from pydantic_handler_converter import BasePydanticFormHandlers
>>>
>>>
>>> class TicketHandlers(BasePydanticFormHandlers[TicketSchema]):
...     pass
... 
...     
#-----------------method-that-will-run-after-schema-filling-out------------------
>>> from aiogram.fsm.context import FSMContext
>>> from aiogram.types import Message
>>> from pydantic_handler_converter.types import Event
>>>
>>>
>>> async def final_callable(data: TicketSchema, event: Event, _: FSMContext):
...     return await event.answer(f"Your final schema data: {data.json()}")
... 
... 
#------------------------creation-of-main-polling-method-------------------------
>>> from aiogram import Router, Bot, Dispatcher
>>> from aiogram.filters.command import Command as CommandFilter
>>>
>>>
>>> async def main():
...     router = Router()
...     ticket_hanlders = TicketHandlers(finish_call=final_callable)
...     ticket_hanlders.register2router(router)
... 
...     settings = Settings()  # type: ignore
...     bot = Bot(token=settings.BOT_TOKEN)
... 
...     @router.message(CommandFilter('start'))
...     async def start(message: Message, state: FSMContext):
...         return await ticket_hanlders.next(message, state)  # type: ignore
... 
...     dp = Dispatcher()
...     dp.include_router(router)
...     await dp.start_polling(bot)
... 
... 
>>> def _main():
...     import sys
...     import logging
...     import asyncio
... 
...     logging.basicConfig(level=logging.INFO, stream=sys.stdout)
...     loop = asyncio.new_event_loop()
...     loop.run_until_complete(main())
...     loop.close()
... 
... 
>>> if __name__ == "__main__":
...     _main()
... 

