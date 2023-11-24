

from typing import Protocol, runtime_checkable
from aiogram.types import Message
from aiogram.types.input_media_document import Optional


FILE_TYPE_NAMES = {'video', 'audio', 'document', 'photo', 'animation', 'voice', 'video_note'}


@runtime_checkable
class FType(Protocol):
    file_id: str
    file_unique_id: str
    file_name: Optional[str] = None
    mime_type: Optional[str] = None


def extract_file_from_message(message: Message) -> Optional[tuple[FType, str]]:
    for name in FILE_TYPE_NAMES:
        if (res := getattr(message, name, None)):
            return res, name

    return None

