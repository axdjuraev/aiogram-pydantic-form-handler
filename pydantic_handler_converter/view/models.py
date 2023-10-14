from pydantic import BaseModel
from .base import BaseView


class ModelsView(BaseView):
    def __init__(self, *args, models_dialects: dict[BaseModel, BaseView], **kwargs) -> None:
        super().__init__(*args, **kwargs)
