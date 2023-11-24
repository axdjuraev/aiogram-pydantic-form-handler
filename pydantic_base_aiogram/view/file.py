from .base import BaseView


class FileView(BaseView):
    @property
    def view_text_format(self):
        if self._is_list:
            return self.dialects.INPUT_STR

        return self.dialects.SEND_FILE

