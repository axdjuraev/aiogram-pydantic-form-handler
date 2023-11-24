import asyncio
from typing import Optional
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message

from pydantic_base_aiogram.types import FType
from pydantic_base_aiogram.utils.proxy.album_message import ProxyAlbumMessage


class AlbumMessageMiddleware(BaseMiddleware):
    def __init__(self, latency: float = 0.01) -> None:
        self.album_data: dict[str, list] = {}
        self.latency = latency
        self.bot: Optional[Bot] = None
        super().__init__()

    async def __call__(self, handler, message: Message, data):
        if message.content_type not in FType:
            return await handler(message, data)

        if not self.bot:
            self.bot = data['state'].bot

        key = message.media_group_id or str(message.message_id)
        doc = message

        try:
            self.album_data[key].append(doc)
        except KeyError:
            self.album_data[key] = [doc]
            await asyncio.sleep(self.latency)

            data['_is_last'] = True
            message = self._get_proxified_msg(message, self.album_data[key])
            await handler(message, data)

        if message.media_group_id and data.get("_is_last"):
            del self.album_data[key]
            del data['_is_last']

        return await super().__call__(handler, message, data)

    def _get_proxified_msg(self, message: Message, album: list):
        return ProxyAlbumMessage(
            **{
                **message.dict(),
                'album': album,
                'bot': self.bot,
            }
        )

