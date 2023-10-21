from enum import Enum
from .base import BaseFieldFactory


class EnumFieldFactory(BaseFieldFactory):
    def create4enummeta(self, field, parents, **kwargs):
        return self.create4type(field, parents, force_type=Enum, **kwargs)

