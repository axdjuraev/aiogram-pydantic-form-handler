from .base import BaseView


class IntView(BaseView):
    @property
    def view_text_format(self):
        return self.dialects.INPUT_INT

