from aiogram import Router
from aiogram.filters.state import StateFilter

from pydantic_base_aiogram.types import Event
from pydantic_base_aiogram.field_factory.base import logger
from pydantic_base_aiogram.exceptions import DataValidationError
from pydantic_base_aiogram.utils.proxy.album_message import ProxyAlbumMessage

from .base import BaseController


class FileController(BaseController):
    async def format_data(self, self_, event: Event[ProxyAlbumMessage], _):
        print(f"{event._event=}")

        if not hasattr(event._event, 'album'):
            raise NotImplementedError(f'`{self.__class__.__name__}` requires `AlbumMiddleware` for usage')

        if not self._is_list:
            if len(event._event.album) > 1:
                raise DataValidationError(self.dialects.REQUIRED_ONLY_ONE_FILE)

            return event._event.album[-1]

        return event._event.album 

    def register2router(self, router: Router) -> Router:
        router.message(StateFilter(self.state))(self.__call__)

        logger.debug(f"[{self.__class__.__name__}][register2router]: {locals()=};")
        return router

