from aiogram import F, Router
from aiogram.filters.state import StateFilter

from pydantic_base_aiogram.types import Event
from pydantic_base_aiogram.field_factory.base import logger
from pydantic_base_aiogram.exceptions import DataValidationError, RequireContiniousMultipleError
from pydantic_base_aiogram.utils.proxy.album_message import ProxyAlbumMessage
from pydantic_base_aiogram.abstract_handler import AbstractPydanticFormHandlers as THandler

from .base import BaseController


class FileController(BaseController):
    async def format_data(self, self_: THandler, event: Event[ProxyAlbumMessage], state):
        if not hasattr(event._event, 'album'):
            raise NotImplementedError(f'`{self.__class__.__name__}` requires `AlbumMiddleware` for usage')

        if not self._is_list:
            if len(event._event.album) > 1:
                raise DataValidationError(self.dialects.REQUIRED_ONLY_ONE_FILE)

            return event._event.album[-1]

        await self_._add_state_files(state, event._event.album)
        raise RequireContiniousMultipleError(value=event._event.album)

    def register2router(self, router: Router) -> Router:
        sf = StateFilter(self.state)

        router.message(sf)(self.__call__)
        router.callback_query(F.data == self.dialects.READY_BUTTON_DATA, sf)(self.ready_controller)

        logger.debug(f"[{self.__class__.__name__}][register2router]: {locals()=};")
        return router

