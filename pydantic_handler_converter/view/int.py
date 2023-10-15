from .base import BaseView


class IntView(BaseView):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.text = self.dialects.INPUT_INT.format(field_name=self.field.name)

