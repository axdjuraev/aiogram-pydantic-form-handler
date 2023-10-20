from .base import BaseView


class IntView(BaseView):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.text = (
            self.field.field_info.extra.get('view_text') 
            or self.dialects.INPUT_INT.format(field_name=self.field_name)
        )

