from typing import Optional
from pydantic import BaseModel, Field
from .enums import InputFormTypesEnum 


class InputSchema(BaseModel):
    field_name: str = Field(view_text='Введите название поля')
    view_text: str = Field(view_text='Введите отображаемый текст')
    type: InputFormTypesEnum = Field(view_text='Выберите тип полья')
    is_list: bool = Field(view_text='Является ли данный тип списком')
    extra_keys: Optional[list[str]] = Field(
        view_text='Введите дополнительные кнопки разделенные новой строкой',
        seperator_symbol=('\n', 'New Line')
    )


class SchemaBuilderSchema(BaseModel):
    name: str = Field(view_text='Введите название формы')
    fields: list[InputSchema] 

