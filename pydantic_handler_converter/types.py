from typing import Any, Callable, Generic, Optional, Protocol, TypeVar, Union, runtime_checkable


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
        self.answer = event.message.edit_text if isinstance(event, EditAbleEvent) else event.answer

