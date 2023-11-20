from pydantic.fields import ModelField


class NormalizedModelField:
    
    def __init__(
        self, 
        field: ModelField, 
        field_type: type,
        types: tuple[type], 
        mro_search_key: tuple[type],
        is_list: bool,
    ) -> None:
        self._field = field
        self._types = types
        self.is_list = is_list
        self.mro_search_key = mro_search_key
        self.field_type = field_type
    
    @property
    def is_complex(self):
        return len(self._types) > 1

