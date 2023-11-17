## Schema-State

State for every field and subfields of Schema


```python
>>> from typing import Union
>>> from pydantic import BaseModel
>>> from pydantic_base_aiogram.utils.schema_states import SchemaStates
>>> 
>>> 
>>> class A(BaseModel):
...     a: int
...     b: float
>>> 
>>> 
>>> class B(BaseModel):
...     a: str
...     b: int
>>> 
>>> 
>>> class C(BaseModel):
...     a: Union[A, B]
...     b: int
>>> 
>>> 
>>> res = SchemaStates.create(C) 
>>> assert isinstance(res, SchemaStates) 
>>> assert all(map(lambda x: x in dir(res), ['a', 'b']))
>>> assert isinstance(res.a, SchemaStates) 
>>> assert all(map(lambda x: x in dir(res.a), ['a', 'b']))

``` 

