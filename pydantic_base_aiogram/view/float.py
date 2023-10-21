from .base import BaseView


class FloatView(BaseView):
    @property
    def view_text_format(self):
        return self.dialects.INPUT_FLOAT

