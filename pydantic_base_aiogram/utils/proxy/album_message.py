from typing import Optional
from aiogram import Bot
from aiogram.types import Message
from pydantic import BaseModel, Field
from pydantic_base_aiogram.utils.middleware.type_album import Album


class ProxyAlbumMessage(Message, BaseModel):
    album: Album = Field(default_factory=Album)
    bot: Optional[Bot] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    async def copy_to(self, chat_id: int, *args, **kwargs):
        if self.album and self.bot:
            msg = None
            reply_id = kwargs.get('reply_to_message_id')

            if caption := kwargs.pop('caption', None):
                msg = await self.bot.send_message(chat_id, caption, **kwargs)  # type: ignore
                reply_id = msg.message_id

            if self.album._items:
                media = [x.get_as_input_media() for x in self.album._items]
                album_messages = await self.bot.send_media_group(chat_id, media=media, reply_to_message_id=reply_id)
                return album_messages[0]

            return msg
        
        return await super().copy_to(chat_id, *args, **kwargs)

