## Example with nested schema


```python
>>> #--------------------------nested-juridic-detail-schema--------------------------
>>> from typing import Optional, Union
>>> from pydantic import BaseModel, Field
>>> 
>>> 
>>> class BaseJuridicDetailSchema(BaseModel):
...     phone: str
...     
...     
>>> class JuridicDetailSchema(BaseJuridicDetailSchema):
...     inn: str
...     
...    
>>> class ForeignJuridicDetailSchema(BaseJuridicDetailSchema):
...     foreign_epayment_method: str = Field(description="Электронный способ платежа (это может быть номер карты или номер счета)")
...     foreign_registration_number: Optional[str] = Field(description="Регистрационный номер лица")
...     foreign_inn: str = Field(description="Номер налогоплательщика или его аналог для иностранного контрагента")
...     foreign_oksm_country_code: str = Field(description="Идентификатор страны по справочнику ОКСМ (латиницей)")
... 
... 
>>> #----------------------------------main-schema-----------------------------------
>>> from uuid import uuid4 
>>> 
>>> 
>>> class ContragentSchema(BaseModel):
...     juridical_details: Union[JuridicDetailSchema, ForeignJuridicDetailSchema] = Field(description='Юридические реквизиты')
...     external_id: str = Field(default_factory=lambda: str(uuid4()))
...     name: str
...     rs_url: Optional[str] = None
... 
... 
>>> #----------------------------creating-handlers-group-----------------------------
>>> from pydantic_handler_converter import BasePydanticFormHandlers
>>>
>>>
>>> class ContragentCreationHandlers(BasePydanticFormHandlers[ContragentSchema]):
...     pass
... 
...     
>>> #-----------------method-that-will-run-after-schema-filling-out------------------
>>> from aiogram.fsm.context import FSMContext
>>> from aiogram.types import Message
>>> from pydantic_handler_converter.types import Event
>>>
>>>
>>> async def final_callable(data: ContragentSchema, event: Event, _: FSMContext):
...     return await event._event.edit_text(f"Your final schema data: {data.json()}")
... 
... 
>>> #-----------------------initialization-&-starting-polling------------------------
>>> from example.runner import main, Settings
>>> 
>>> main(ContragentCreationHandlers(finish_call=final_callable), settings=Settings())
>>> 

```

