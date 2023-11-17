## Field Normalization

This process converts complex and duplicated types of field
into light and unique types. e.g to fix this problem:


```python
>>> from typing import Union, List
>>> 
>>> # ----------------------Union------------------------
>>> type(Union[int, float])
<class 'typing._UnionGenericAlias'>
>>> type(int | float)
<class 'types.UnionType'>
>>> 
>>> # ----------------------List------------------------
>>> type(List[int])
<class 'typing._GenericAlias'>
>>> type(list[int])
<class 'types.GenericAlias'>
>>> 
>>> List[int] == list[int]
False

```

