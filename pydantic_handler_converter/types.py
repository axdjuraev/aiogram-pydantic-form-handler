from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Optional, Protocol, TypeVar, Union, runtime_checkable
from aiogram import Router


@runtime_checkable
class KeyboardItem(Protocol):
    @property
    def text(self):
        raise NotImplementedError

    @property
    def data(self):
        raise NotImplementedError


@runtime_checkable
class GetterField(Protocol):
    async def getter(self) -> list[KeyboardItem]:
        raise NotImplementedError


@runtime_checkable
class DataGetterCallable(Protocol):
    async def __call__(self) -> list[KeyboardItem]:
        raise NotImplementedError


@runtime_checkable
class ExtraStringField(Protocol):
    async def is_extra_str(self) -> bool:
        raise NotImplementedError


@runtime_checkable
class BindAbleCallable(Protocol):
    def bind(self, elem):
        raise NotImplementedError


class BaseSingleHandler(ABC, BindAbleCallable):
    name: str
    step_name: str
    is_custom: bool

    def __init__(self) -> None:
        self.is_custom = False

    @abstractmethod
    async def __call__(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def register2router(self, router: Router):
        raise NotImplementedError

    @abstractmethod
    def bind(self, elem) -> 'BaseSingleHandler':
        return super().bind(elem)


@runtime_checkable
class DescriptiveEnum(Protocol):
    @property
    def name(self):
        raise NotImplementedError

    @property
    def description(self):
        raise NotImplementedError


@runtime_checkable
class AnswerAbleEvent(Protocol):
    async def answer(self, text, reply_markup: Union[None, Any] = None):
        raise NotImplementedError


@runtime_checkable
class MessageEvent(Protocol):
    async def edit_text(self, text, reply_markup: Union[None, Any] = None):
        raise NotImplementedError


@runtime_checkable
class EditAbleEvent(Protocol):
    @property
    def message(self) -> MessageEvent:
        raise NotImplementedError


TCallableElem = TypeVar('TCallableElem', bound=Callable)


class CallableWithNext(Generic[TCallableElem]):
    def __init__(self, elem: TCallableElem, next: Optional[TCallableElem] = None) -> None:
        self.elem = elem
        self._next = next

    async def next(self, *args, **kwargs):
        if not self._next:
            raise NotImplementedError

        return await self._next(*args, **kwargs)


TEvent = Union[EditAbleEvent, AnswerAbleEvent]


class Event:
    def __init__(self, event: Union[AnswerAbleEvent, EditAbleEvent]) -> None:
        self._event = event
        self._answer = event.message.edit_text if isinstance(event, EditAbleEvent) else event.answer
        self.default_parse_mode = 'Markdown'

    async def answer(self, text: str, *, reply_markup = None, **kwargs):
        kwargs['parse_mode'] = kwargs.get('parse_mode', self.default_parse_mode)

        return await self._answer(text, reply_markup=reply_markup, **kwargs)

