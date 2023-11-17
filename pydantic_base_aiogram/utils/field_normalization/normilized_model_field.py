from pydantic.fields import ModelField


class NormalizedModelField:
    is_list: bool
    types: list[type]
    unique_types: list[type]
    
    def __init__(self, field: ModelField, types: list[type], is_list: bool) -> None:
        self._field = field
        self.types = types
        self.is_list = is_list
        self.unique_types = sorted(set(self.types), key=lambda x: x.__name__)
    
    @property
    def is_complex(self):
        return len(self.types) > 1

