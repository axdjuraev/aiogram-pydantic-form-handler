from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Optional, Protocol, TypeVar, Union, runtime_checkable
from aiogram import Router


class KeyboardItem(dict):
    """
        key: callback_data
        value: text
    """


@runtime_checkable
class GetterField(Protocol):
    async def getter(self) -> KeyboardItem:
        raise NotImplementedError


@runtime_checkable
class DataGetterCallable(Protocol):
    async def __call__(self) -> KeyboardItem:
        raise NotImplementedError


@runtime_checkable
class ExtraStringField(Protocol):
    @property
    def is_extra_str(self) -> bool:
        raise NotImplementedError


@runtime_checkable
class BindAbleCallable(Protocol):
    def bind(self, elem):
        raise NotImplementedError


class BaseSingleHandler(ABC, BindAbleCallable):
    name: str
    step_name: str
    is_custom: bool
    tree_id: Optional[int] = None

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
    def __init__(
        self, elem: TCallableElem, 
        next: Optional['CallableWithNext'] = None,
        previos: Optional['CallableWithNext'] = None,
    ) -> None:
        self.elem = elem
        self._next = next
        self._previos = previos

    def set_next(self, next: 'CallableWithNext'):
        self._next = next

    def set_previos(self, previos: 'CallableWithNext'):
        self._previos = previos

    async def _move(self, move: Optional['CallableWithNext'], args, kwargs):
        if not move:
            raise NotImplementedError

        return await move.elem.__call__(*args, **kwargs)

    async def back(self, *args, **kwargs):
        return await self._move(self._previos, args, kwargs)

    async def next(self, *args, **kwargs):
        return await self._move(self._next, args, kwargs)


TEvent = Union[EditAbleEvent, AnswerAbleEvent]


class Event:
    def __init__(self, event: Union[AnswerAbleEvent, EditAbleEvent]) -> None:
        self._event = event
        self._answer = event.message.edit_text if isinstance(event, EditAbleEvent) else event.answer
        self.default_parse_mode = 'Markdown'

    async def answer(self, text: str, *, reply_markup = None, **kwargs):
        kwargs['parse_mode'] = kwargs.get('parse_mode', self.default_parse_mode)

        return await self._answer(text, reply_markup=reply_markup, **kwargs)

