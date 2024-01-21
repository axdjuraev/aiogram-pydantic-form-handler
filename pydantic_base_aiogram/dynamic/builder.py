from uuid import uuid4
from typing import Callable, Optional, Type
from types import new_class
from pydantic import BaseModel, Field
from pydantic_base_aiogram.dynamic.field_metadata import FieldMetadata
from pydantic_base_aiogram.main import SchemaBaseHandlersGroup
from pydantic_base_aiogram.types import FileType


class DynamicHandlersGroupBuilder:
    _DEFAULT_SCHEMA_NAME_POSTFIX = "Schema"
    _DEFAULT_TSCHEMA_BASEMODEL = BaseModel
    _DEFAULT_EXTRA_TYPES = {
        FileType.__name__: FileType,
    }

    def __init__(
        self, 
        field_metadas: list[FieldMetadata], 
        getters: Optional[dict[str, Callable]] = None,
        extra_schema: Optional[list[BaseModel]] = None,
        extra_types: Optional[dict[str, type]] = None,
        extra_props: Optional[dict] = None,
        schema_name_postfix: Optional[str] = None,
        TSchemaBaseModel: Optional[Type[BaseModel]] = None,
    ) -> None:
        self._field_metadas = field_metadas
        self._getters = getters or {}
        self._extra_types = extra_types or {}
        self._extra_types.update(self._DEFAULT_EXTRA_TYPES)
        self._schemas = extra_schema.copy() if extra_schema else []
        self._schema_name_postfix = schema_name_postfix or self._DEFAULT_SCHEMA_NAME_POSTFIX
        self._TSchemaBaseModel = TSchemaBaseModel or self._DEFAULT_TSCHEMA_BASEMODEL
        self._extra_props = extra_props
        self._check_getters()

    def _check_getters(self):
        for meta in self._field_metadas:
            assert (
                not meta._getter_name 
                or meta._getter_name in self._getters
            ), f"Getter `{meta._getter_name}` not found!"
            assert self._load_type(meta._type) is not None, f"Type `{meta._type}` not found!"

    def _body_exec_extra_props(self, n: dict):
        if not self._extra_props:
            return

        n.update(self._extra_props)

    def build(
        self, 
        name: Optional[str] = None
    ) -> tuple[Type[BaseModel], Type[SchemaBaseHandlersGroup]]:
        name = name or str(uuid4())
        schema_name = f"{name}{self._schema_name_postfix}"
        TSchema = self._build_schema(schema_name)

        TRes = new_class(
            name, 
            bases=(SchemaBaseHandlersGroup[TSchema],), 
            kwds={'back_data': ...},
            exec_body=self._body_exec_extra_props,
        ) 

        return (TSchema, TRes)

    def _create_dump_returner(self, extra_keys: dict):
        async def dump_returner(*_):
            return extra_keys

        return dump_returner

    def _build_schema(self, schema_name: Optional[str] = None) -> Type[BaseModel]:
        schema_name = schema_name or str(uuid4())
        properties = {}
        types = {}

        for meta in self._field_metadas:
            getter = meta._getter_name and self._getters[meta._getter_name]

            if meta._extra_keys and not getter:
                getter = self._create_dump_returner(meta._extra_keys)

            field = Field(view_text=meta._view_text, getter=getter)
            properties[meta._field_name] = field
            types[meta._field_name] = self._load_type(meta._type)

        properties['__annotations__'] = types

        return type(schema_name, (self._TSchemaBaseModel,), properties)
    
    def _load_type(self, name: str) -> type:
        try:
            return eval(name)
        except (NameError, TypeError):
            return self._extra_types.get(name)  # type: ignore

