from aiogram.types import Message
from pydantic_base_aiogram.exceptions import DataValidationError

from pydantic_base_aiogram.types import Event
from pydantic_base_aiogram.utils.file import extract_file_from_message
from pydantic_base_aiogram.utils.proxy.album_message import ProxyAlbumMessage

from .base import BaseController


class FileController(BaseController):
    async def format_data(self, self_, event: Event[Message], _):
        if not isinstance(event._event, ProxyAlbumMessage):
            raise NotImplementedError(f'`{self.__class__.__name__}` requires `AlbumMiddleware` for usage')

        input_files = []
        
        for file_message in event._event.album:
            input_file = extract_file_from_message(file_message)

            if input_file:
                input_files.append(input_file)

        if not self._is_list:
            if len(input_files) > 1:
                raise DataValidationError(self.dialects.REQUIRED_ONLY_ONE_FILE)

            return input_files[-1]

        return input_files

