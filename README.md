# Pydantic-base-aiogram

This code simplifies the conversion of Pydantic schemas into Aiogram handler groups, 
making it easy to create form-filling handlers.

## Installation
```bash
    pip install pydantic_base_aiogram
```

## Usage:

```python
>>> from enum import Enum
>>> from typing import Union
>>> from pydantic import BaseModel
>>> from pydantic_base_aiogram import SchemaBaseHandlersGroup

# ----------------------------------------utils-methods--------------------------------------

>>> def check_for_properties_existense(cls, properties: list[str]):
...     dirs = dir(cls)
...     assert len(tuple(filter(lambda x: not x in dirs, properties))) == 0
...     assert cls(finish_call=None)

# ----------------------------------------Simple datatypes schema--------------------------------------

>>> class PersonPydanticFormSchema(BaseModel):
...     name: str
...     age: int
...     height: float 
... 

>>> class PersonFormHanlders(SchemaBaseHandlersGroup[PersonPydanticFormSchema]):
...     pass
...
...
>>> check_for_properties_existense(PersonFormHanlders, ['name_view', 'age_view', 'height_view'])

# ----------------------------------------Enum datatype schema-----------------------------------------

>>> class Mood(Enum):
...     HAPPY = "😄 Happy"
...     SAD = "😢 Sad"
...     EXCITED = "🤩 Excited"
...     RELAXED = "😌 Relaxed"
...
>>>
>>>
>>> class PersonMoodPydanticFormSchema(BaseModel):
...     name: str
...     current_mood: Mood
...
>>> class PersonMoodFormHanlders(SchemaBaseHandlersGroup[PersonMoodPydanticFormSchema]): 
...     pass
...
...
>>> check_for_properties_existense(PersonMoodFormHanlders, ['name_view', 'current_mood_view'])

# ----------------------------------------Complex schema-----------------------------------------------

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
>>> class PersonFormHanlders(SchemaBaseHandlersGroup[Person]): 
...     pass
...
...
>>> check_for_properties_existense(
...     PersonFormHanlders, 
...     [
...         'name_view', 
...         'address_street_view', 
...         'address_city_view', 
...         'address_postal_code_view'
...     ]
... )
...

# ------------------------------------Combined Enum datatype schema------------------------------------

>>> class HappyMood(Enum):
...     HAPPY = "😄 Happy"
...
>>> class SadMood(Enum):
...     SAD = "😢 Sad"
...
>>> class ExcitedMood(Enum):
...     EXCITED = "🤩 Excited"
...
>>> class RelaxedMood(Enum):
...     RELAXED = "😌 Relaxed"
...
>>>
>>> class PersonMoodPydanticFormSchema(BaseModel):
...     name: str
...     current_mood: Union[HappyMood, SadMood, ExcitedMood, RelaxedMood]
...     future_mood: HappyMood | SadMood | ExcitedMood | RelaxedMood
...
...
>>> class PersonMoodFormHanlders(SchemaBaseHandlersGroup[PersonMoodPydanticFormSchema]): 
...     pass
...
...
>>> check_for_properties_existense(PersonMoodFormHanlders, ['name_view', 'current_mood_view'])

```

