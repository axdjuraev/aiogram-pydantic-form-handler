from typing import TYPE_CHECKING
from pydantic_base_aiogram.types import Event, OptionalAlbum, OptionalFile
from pydantic_base_aiogram.exceptions import DataValidationError, RequireContiniousMultipleError
from pydantic_base_aiogram.utils.proxy.album_message import ProxyAlbumMessage
from .file import FileController


if TYPE_CHECKING:
    from pydantic_base_aiogram.main import SchemaBaseHandlersGroup as THandler


class OptionalFileController(FileController):
    async def format_data(self, self_: "THandler", event: Event[ProxyAlbumMessage], state):
        if not hasattr(event._event, 'album'):
            raise NotImplementedError(f'`{self.__class__.__name__}` requires `AlbumMiddleware` for usage')

        if not self.field.type_ is OptionalAlbum:
            if len(event._event.album._items) > 1:
                raise DataValidationError(self.dialects.REQUIRED_ONLY_ONE_FILE)

            if (file := (event._event.album and event._event.album[-1])):
                await self_._add_state_files(self.step_name, event._event.album, state)

            return OptionalFile(
                item=file,
                html_content_text=event._event.html_text,
            )

        album = await self_._get_state_files(self.step_name, state)

        if event._event.album._items:
            album.extend(event._event.album)
            await self_._add_state_files(self.step_name, album, state)

        res = OptionalAlbum(
            album=album,
            html_content_text=event._event.html_text,
        )

        if (old_one := await self._getvalue(self.data_key, state)):
            old_one.extend(res)
            res = old_one

        raise RequireContiniousMultipleError(value=res)
