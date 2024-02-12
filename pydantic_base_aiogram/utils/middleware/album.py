import asyncio
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from pydantic_base_aiogram.types import FType, FileType
from pydantic_base_aiogram.utils.file import extract_file_from_message
from pydantic_base_aiogram.utils.proxy.album_message import ProxyAlbumMessage


class AlbumMessageMiddleware(BaseMiddleware):
    def __init__(self, latency: float = 0.1) -> None:
        self.album_data: dict[str, list] = {}
        self.latency = latency
        super().__init__()

    async def __call__(self, handler, message: Message, data):
        if message.content_type not in FType:
            return await handler(message, data)

        state = data['state']
        key = message.media_group_id or str(message.message_id)
        doc = self._get_message_as_doc(message)

        try:
            self.album_data[key].append(doc)
        except KeyError:
            self.album_data[key] = [doc]
            await asyncio.sleep(self.latency)

            data['_is_last'] = True
            message = self._get_proxified_msg(message, self.album_data[key], state)
            await handler(message, data)

        if message.media_group_id and data.get("_is_last"):
            del self.album_data[key]
            del data['_is_last']

        return await super().__call__(handler, message, data)

    def _get_message_as_doc(self, message: Message):
        if not (file := extract_file_from_message(message)):
            return

        file, type_name = file

        return FileType(
            file_id=file.file_id,
            file_unique_id=file.file_unique_id,
            file_name=str(getattr(file, 'file_name', file.file_id)),
            mime_type=str(getattr(file, 'mime_type', 'image/jpeg')),
            content_type=type_name,
            msg=message,
        )

    def _get_proxified_msg(self, message: Message, album: list, state: FSMContext):
        return ProxyAlbumMessage(
            **{
                **message.dict(),
                'album': album,
                'bot': state.bot,
            }
        )
