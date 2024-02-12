from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Iterable, Optional, Protocol, TypeVar, Union, runtime_checkable
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from pydantic import BaseModel as _BaseSchema
from pydantic.fields import ModelField

from pydantic_base_aiogram.utils.abstractions import is_list_type
from pydantic_base_aiogram.utils.step import get_step_name
from pydantic_base_aiogram.dialecsts import BaseDialects


class KeyboardItem(dict):
    """
        key: callback_data
        value: text
    """


@runtime_checkable
class Referencer(Protocol):
    def _ref_data_getter(self) -> Any:
        pass


@runtime_checkable
class ReferenceRegister(Protocol):
    def __call__(self, referencer: Any, _getter_name: str) -> Any:
        raise NotImplementedError


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
    async def __call__(self, state: FSMContext, page: int = 1, page_size: int = 10) -> KeyboardItem:
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
    _DEFAULT_TEXT_SEPRATOR_SYMBOL = ('\n', 'новой строкой')

    name: str
    step_name: str
    is_custom: bool
    tree_id: Optional[int] = None
    _back_data_getter: Callable
    back_data = None

    def __init__(
        self,
        field: ModelField,
        dialects: BaseDialects,
        parents: Iterable[str],
        tree_id: Optional[int] = None,
        tree_head_step_name: Optional[str] = None,
        is_has_back: Optional[str] = None,
        back_data: Optional[str] = None,
        name_format: str = "{step_name}",
        back_allowed: bool = True,
        base_cq_prefix: str = "_",
        data_key: Optional[str] = None,
        is_list_item: bool = False,
        text_seperator_symbol: Optional[tuple[str, str]] = None,
        state_base_manage: bool = False, 
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
        self._back_data_getter: Callable = back_data  # type: ignore
        self.back_allowed = back_allowed
        self.base_cq_prefix = base_cq_prefix
        self.is_list_item = is_list_item
        self.data_key = (
            data_key
            or field.field_info.extra.get('data_key')
            or self.field.name
        )
        self._is_list = is_list_type(self.field.outer_type_)
        self._text_seperator_symbol = (
            text_seperator_symbol  
            or self.field.field_info.extra.get('seperator_symbol') 
            or self._DEFAULT_TEXT_SEPRATOR_SYMBOL
        )

        if isinstance(back_data, ReferenceRegister):
            back_data(self, '_back_data_getter')
            self.__class__.back_data
        else:
            self.back_data = back_data
            self.back_data_getter = None

        self._is_state_base_manage = state_base_manage

    def back_data_getter(self): 
        return self._back_data_getter() 

    async def _setvalue(self, value, state: FSMContext, *, key: Optional[str] = None):
        data_key = key or self.data_key
        data = await state.get_data()
        parent_elem = data

        for parent_name in self.parents:
            parent = parent_elem.get(parent_name)

            if parent is None:
                if self.is_list_item:
                    parent = []
                else:
                    parent = {}

                parent_elem[parent_name] = parent

            if isinstance(parent, list):
                if len(parent) < 1:
                    parent.append({})
                elif data_key in parent[-1]:
                    parent.append({})

                parent = parent[-1]

            parent_elem = parent

        if not is_list_type(self.field.outer_type_):
            parent_elem[data_key] = value
        else:
            elems = parent_elem.get(data_key, [])

            if isinstance(value, Iterable):
                elems.extend(value)
            else:
                elems.append(value)

            parent_elem[data_key] = elems

        await state.update_data(**data)

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
    def short_name(self):
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

    def set_next(self, next: Optional['CallableWithNext']):
        self._next = next

    def set_previos(self, previos: Optional['CallableWithNext']):
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

    async def answer(self, text: str, state: Optional[FSMContext] = None, *, reply_markup: Optional[InlineKeyboardMarkup] = None, **kwargs):
        if state and not isinstance(self._event, EditAbleEvent):
            await self.clear_stack(state)

        if not reply_markup or not reply_markup.inline_keyboard:
            reply_markup = None

        kwargs['parse_mode'] = kwargs.get('parse_mode', self.default_parse_mode)
        res = await self._answer(text, reply_markup=reply_markup, **kwargs)

        if reply_markup and state and hasattr(res, 'message_id'):
            await self.add_stack_message(state, getattr(res, 'message_id'))

        return res


FType = [
    types.ContentType.DOCUMENT, 
    types.ContentType.PHOTO, 
    types.ContentType.AUDIO, 
    types.ContentType.VIDEO,
    types.ContentType.VIDEO_NOTE,
    types.ContentType.VOICE,
    types.ContentType.STICKER,
    types.ContentType.ANIMATION,
]


class FileType(_BaseSchema):
    file_id: str
    file_unique_id: str
    file_name: str
    mime_type: str
    content_type: Optional[str] = None
    msg: Message
        
    def get_as_input_media(self):
        TMedia = getattr(types, f"InputMedia{str(self.content_type).title()}", types.InputMediaDocument)
        return TMedia(
            media=self.file_id,
            type=self.msg.content_type,
            parse_mode='Markdown',
        )

