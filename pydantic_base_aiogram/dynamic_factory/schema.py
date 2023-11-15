from pydantic import BaseModel, Field
from .enums import InputFormTypesEnum 


class InputSchema(BaseModel):
    view_text: str = Field(view_text='Введите отображаемый текст')
    type: InputFormTypesEnum = Field(view_text='Выберите тип полья')
    is_list: bool = Field(view_text='Является ли данный тип списком')


class SchemaBuilderSchema(BaseModel):
    name: str = Field(view_text='Введите название формы')
    fields: list[InputSchema] 

