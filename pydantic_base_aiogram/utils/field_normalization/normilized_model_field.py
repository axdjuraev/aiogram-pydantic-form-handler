from pydantic.fields import ModelField


class NormalizedModelField(ModelField):
    is_list: bool
    types: list[type]
    unique_types: list[type]
    
    @property
    def is_complex(self):
        return len(self.types) > 1

