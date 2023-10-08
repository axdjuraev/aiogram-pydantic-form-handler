from typing import Any, Protocol, Union, runtime_checkable


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


TEvent = Union[EditAbleEvent, AnswerAbleEvent]


class Event:
    def __init__(self, event: Union[AnswerAbleEvent, EditAbleEvent]) -> None:
        self.answer = event.message.edit_text if isinstance(event, EditAbleEvent) else event.answer

