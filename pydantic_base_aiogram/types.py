from abc import ABC, abstractmethod
from typing import Any, Generic, Iterable, Optional, Protocol, TypeVar, Union, runtime_checkable
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from pydantic.fields import ModelField
from pydantic_base_aiogram.utils.step import get_step_name
from pydantic_base_aiogram.dialecsts import BaseDialects
from aiogram import Router


class KeyboardItem(dict):
    """
        key: callback_data
        value: text
    """


@runtime_checkable
class DescriptiveSchema(Protocol):
    @property
    def __NAME__(self):
        raise NotImplementedError


@runtime_checkable
class GetterField(Protocol):
    async def getter(self, state: FSMContext) -> KeyboardItem:
        raise NotImplementedError


@runtime_checkable
class DataGetterCallable(Protocol):
    async def __call__(self, state: FSMContext) -> KeyboardItem:
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

    def __init__(
        self,
        field: ModelField, 
        dialects: BaseDialects, 
        parents: Iterable[str], 
        tree_id: Optional[int] = None,
        tree_head_step_name: Optional[str] = None,
        is_has_back: Optional[str] = None,
        name_format: str = "{step_name}",
        back_allowed: bool = True,
        base_cq_prefix: str = "_",
        extra_keys: Optional[str] = None,
        **_,
    ) -> None:
        self.field = field
        self.step_name = get_step_name(field, parents)
        self.name = name_format.format(step_name=self.step_name)
        self.dialects = dialects
        self.parents = parents
        self.is_custom = False
        self.tree_id = tree_id
        self.tree_head_step_name = tree_head_step_name
        self.is_has_back = is_has_back
        self.back_allowed = back_allowed
        self.base_cq_prefix = base_cq_prefix

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


class CallableWithNext:
    def __init__(
        self, elem: BaseSingleHandler, 
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


TEvent = TypeVar('TEvent', bound=Union[EditAbleEvent, AnswerAbleEvent, Message, CallbackQuery])


class Event(Generic[TEvent]):
    def __init__(self, event: TEvent) -> None:
        self._event = event
        self._answer = event.message.edit_text if isinstance(event, EditAbleEvent) else event.answer
        self.default_parse_mode = 'Markdown'

    async def _get_stack(self, state: FSMContext):
        return (await state.get_data()).get('__stack__', [])

    async def _set_stack(self, state: FSMContext, val):
        await state.update_data(__stack__=val)

    async def add_stack_message(self, state: FSMContext, message_id: int):
        stack = await self._get_stack(state)
        stack.append(message_id)
        await self._set_stack(state, stack)

    async def clear_stack(self, state: FSMContext):
        for message_id in await self._get_stack(state):
            try:
                await state.bot.edit_message_reply_markup(state.key.chat_id, message_id)
            except Exception:
                pass

        await self._set_stack(state, [])

    async def answer(self, text: str, state: Optional[FSMContext] = None, *, reply_markup = None, **kwargs):
        if state and isinstance(self._event, AnswerAbleEvent):
            await self.clear_stack(state)

        kwargs['parse_mode'] = kwargs.get('parse_mode', self.default_parse_mode)
        res = await self._answer(text, reply_markup=reply_markup, **kwargs)

        if reply_markup and state and hasattr(res, 'message_id'):
            await self.add_stack_message(state, getattr(res, 'message_id'))

        return res

