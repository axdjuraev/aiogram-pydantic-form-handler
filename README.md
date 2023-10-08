# Pydantic-handler-converter

This code simplifies the conversion of Pydantic schemas into Aiogram handler groups, 
making it easy to create form-filling handlers.

## Installation
```bash
    pip install pydantic_handler_converter
```

## Usage:

```python
>>> from enum import Enum
>>> from pydantic import BaseModel
>>> from pydantic_handler_converter import BasePydanticFormHandlers
>>>
>>> # Simple datatypes schema 
>>> class PersonPydanticFormSchema(BaseModel):
...     name: str
...     age: int
...     height: float 
... 

>>> class PersonFormHanlders(BasePydanticFormHandlers[PersonPydanticFormSchema]):
...     pass
...
...
>>> assert PersonFormHanlders.Schema == PersonPydanticFormSchema
>>> dirs = dir(PersonFormHanlders)
>>> assert len(tuple(filter(lambda x: not x in dirs, ['_name_view', '_age_view', '_height_view']))) == 0


>>> class Mood(Enum):
...     HAPPY = "😄 Happy"
...     SAD = "😢 Sad"
...     EXCITED = "🤩 Excited"
...     RELAXED = "😌 Relaxed"
...
>>>
>>>
>>>  # Enum datatype schema
>>> class PersonMoodPydanticFormSchema(BaseModel):
...     name: str
...     current_mood: Mood
...
>>> class PersonMoodFormHanlders(BasePydanticFormHandlers[PersonMoodPydanticFormSchema]): 
...     pass
...
...
>>> assert PersonMoodFormHanlders.Schema == PersonMoodPydanticFormSchema
>>> dirs = dir(PersonMoodFormHanlders)
>>> assert len(tuple(filter(lambda x: not x in dirs, ['_name_view', '_current_mood_view']))) == 0

```
