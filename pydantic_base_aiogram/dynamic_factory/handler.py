from pydantic_base_aiogram.dialecsts import RuDialects
from pydantic_base_aiogram.main import SchemaBaseHandlersGroup
from .schema import SchemaBuilderSchema


class SchemaBuilderHandlers(SchemaBaseHandlersGroup[SchemaBuilderSchema]):
    DIALECTS = RuDialects()

