from aiogram import F, Router
from aiogram.filters.state import StateFilter

from pydantic_base_aiogram.types import Event
from pydantic_base_aiogram.field_factory.base import logger
from pydantic_base_aiogram.exceptions import DataValidationError, RequireContiniousMultipleError
from pydantic_base_aiogram.utils.middleware.type_album import Album
from pydantic_base_aiogram.utils.proxy.album_message import ProxyAlbumMessage
from pydantic_base_aiogram.abstract_handler import AbstractPydanticFormHandlers as THandler

from .base import BaseController


class FileController(BaseController):
    async def format_data(self, self_: THandler, event: Event[ProxyAlbumMessage], state):
        if not hasattr(event._event, 'album'):
            raise NotImplementedError(f'`{self.__class__.__name__}` requires `AlbumMiddleware` for usage')

        if not event._event.album._items:
            DataValidationError(self.dialects.INVALID_TYPE_DATA)

        album = await self_._get_state_files(self.step_name, state)
        album.extend(event._event.album)
        await self_._add_state_files(self.step_name, album, state)

        if not self.field.type_ is Album:
            if len(event._event.album._items) > 1:
                raise DataValidationError(self.dialects.REQUIRED_ONLY_ONE_FILE)

            return event._event.album[-1]

        raise RequireContiniousMultipleError(value=album)

    def register2router(self, router: Router) -> Router:
        sf = StateFilter(self.state)

        router.message(sf)(self.__call__)
        router.callback_query(F.data == self.dialects.READY_BUTTON_DATA, sf)(self.ready_controller)

        logger.debug(f"[{self.__class__.__name__}][register2router]: {locals()=};")
        return router

