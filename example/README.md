```python
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
>>> #----------------------------subject-enum-declaration----------------------------
>>> class SubjectEnum(Enum):
...     FEAT = "feat", "Need to add feature"
...     FIX = "fix", "Resolve issue"
...     REF = "ref", "There is code smell"
...     TEST = "test", "Its doesn't look like be tested"
...     CHOR = "chor", "Bump-version"
...     DOCS = "docs", "There is really hard abstsraction to get into it"
...     STYLE = "style", "Code style doesnt looke good"
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
>>> #---------------------------some-keyboard-items-getter---------------------------
>>> 
>>> async def getter():
...    return {
...        'elem1': 'Elem1',
...        'elem2': 'Elem2',
...        'elem3': 'Elem3',
...    }
... 
... 
>>> #---------------------------actual-schema-declaration----------------------------
>>> from pydantic import BaseModel, Field
>>>
>>>
>>> class TicketSchema(BaseModel):
...     title: str
...     short_description: str
...     priority: PriorityEnum
...     subject: list[SubjectEnum]
...     elem: str = Field(getter=getter, is_extra_str=True)
... 
... 
>>> #--------------------------------using-converter---------------------------------
>>> from pydantic_handler_converter import BasePydanticFormHandlers
>>>
>>>
>>> class TicketHandlers(BasePydanticFormHandlers[TicketSchema]):
...     pass
... 
...     
>>> #-----------------method-that-will-run-after-schema-filling-out------------------
>>> from aiogram.fsm.context import FSMContext
>>> from aiogram.types import Message
>>> from pydantic_handler_converter.types import Event
>>>
>>>
>>> async def final_callable(data: TicketSchema, event: Event, _: FSMContext):
...     return await event._event.edit_text(f"Your final schema data: {data.json()}")
... 
... 
>>> #------------------------creation-of-main-polling-method-------------------------
>>> from example.runner import main
>>> main(TicketHandlers(finish_call=final_callable))

```
