from abc import ABC
from typing import Iterable, Optional
from pydantic.fields import ModelField
from axabc.logging import SimpleFileLogger


logger = SimpleFileLogger('aiogram-pydantic-handler')


class BaseFieldFactory(ABC):
    elem_postfix: str

    def __init_subclass__(cls, elem_postfix: str) -> None:
        cls.elem_postfix = elem_postfix

    def create(self, field: ModelField, parents: Optional[Iterable[str]] = None, **kwargs):
        type_ = field.type_
        base_type_name = type(type_).__name__ 
        logger.debug(f"[{self.__class__.__name__}][create]: {field.name=}; {type_=}; {base_type_name=}")

        try: 
            creator = getattr(self, f'_create_{base_type_name}')
            creator(field, kwargs, parents) 
        except AttributeError:
            raise NotImplementedError(f'`{base_type_name}` is not supported in {self.__class__.__name__}')

    def _create_type(self, field: ModelField, kwargs, parents: Optional[Iterable[str]] = None):
        logger.debug(f"[{self.__class__.__name__}][_create_type]: {field.name=}; {parents=};")

        view_cls = globals().get(f"{field.type_.__name__.title()}{self.elem_postfix}")

        if view_cls is None:
            raise NotImplementedError(f'`{field.type_}` is not supported in {self.__class__.__name__}')

        return view_cls.create(field, parents=parents, **kwargs)

    def _create_modelmetaclass(self, field: ModelField, kwargs, parents: Optional[Iterable[str]] = None):
        logger.debug(f"[{self.__class__.__name__}][_create_modelmetaclass_view]: {field.name=}; {parents=}; {kwargs=};")

