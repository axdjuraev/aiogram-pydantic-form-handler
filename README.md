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
>>> dirs = dir(PersonFormHanlders)
>>> assert len(tuple(filter(lambda x: not x in dirs, ['name_view', 'age_view', 'height_view']))) == 0


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
>>> dirs = dir(PersonMoodFormHanlders)
>>> assert len(tuple(filter(lambda x: not x in dirs, ['name_view', 'current_mood_view']))) == 0



>>>  # Complex schema
>>> class Address(BaseModel):
...     street: str
...     city: str
...     postal_code: str
...
>>> class Person(BaseModel):
...      name: str
...      age: int
...      address: Address
...
...
>>> class PersonFormHanlders(BasePydanticFormHandlers[Person]): 
...     pass
...
...
>>> dirs = dir(PersonFormHanlders)
>>> assert len(tuple(filter(lambda x: not x in dirs, 
...     ['name_view', 'address_street_view', 'address_city_view', 'address_postal_code_view']
... ))) == 0

```
