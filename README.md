# Pydantic-handler-converter

This code simplifies the conversion of Pydantic schemas into Aiogram handler groups, 
making it easy to create form-filling handlers.

# Usage:

```python
>>> from pydantic import BaseModel
>>> from pydantic_handler_converter import BasePydanticFormHandlers
>>> 
>>>
>>> class GreatPydanticFormSchema(BaseModel):
...     name: str
... 

>>> class GreatFormHanlders(BasePydanticFormHandlers[GreatPydanticFormSchema]): pass
... 

>>> assert GreatFormHanlders.Schema == GreatPydanticFormSchema

```
