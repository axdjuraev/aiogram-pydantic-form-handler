## Dynamic capability

It allows to create schemas and handlers at runtime

```python
>>> from pydantic_base_aiogram import SchemaBaseHandlersGroup
>>> from pydantic_base_aiogram.dynamic.builder import DynamicHandlersGroupBuilder
>>> from pydantic_base_aiogram.dynamic.field_metadata import FieldMetadata
>>> 
>>> 
>>> fields_metadata = [FieldMetadata(view_text=k, type=v) for k, v in {'name': 'str', 'age': 'int'}.items()]
>>> Schema, HandlersGroup = DynamicHandlersGroupBuilder(fields_metadata).build('PersonFormHandlers')
>>> assert issubclass(res, SchemaBaseHandlersGroup)

```

