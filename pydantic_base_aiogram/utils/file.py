from aiogram import types
from typing import Protocol, Optional, TypeAlias, Union, runtime_checkable



FILE_TYPE_NAMES = {'video', 'audio', 'document', 'photo', 'animation', 'voice', 'video_note'}


@runtime_checkable
class FType(Protocol):
    file_id: str
    file_unique_id: str
    file_name: Optional[str] = None
    mime_type: Optional[str] = None


TDocument: TypeAlias = Union[
    types.Audio, 
    types.Document,
    types.Video,
    types.Sticker,
    types.Voice,
    types.Animation,
    types.VideoNote,
    types.PhotoSize

]


def extract_file_from_message(message: types.Message) -> Optional[tuple[TDocument, str]]:
    for name in FILE_TYPE_NAMES:
        if (res := getattr(message, name, None)):
            if isinstance(res, list):
                res = res[-1]

            return res, name

    return None

