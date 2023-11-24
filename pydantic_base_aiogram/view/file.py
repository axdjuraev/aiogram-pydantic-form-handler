from .base import BaseView


class FileView(BaseView):
    _IGNORE_LIST_BUTTON = True

    @property
    def view_text_format(self):
        if self._is_list:
            return self.dialects.SEND_FILES

        return self.dialects.SEND_FILE

