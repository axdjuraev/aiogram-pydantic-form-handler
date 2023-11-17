from pydantic.fields import ModelField
from pydantic_base_aiogram.utils.field_normalization.type_normalization import TypeNormilizer as _TypeNormilizer
from pydantic_base_aiogram.utils.field_normalization.normilized_model_field import NormalizedModelField


class FieldNormalizer(_TypeNormilizer):
    def normalize_field(self, field: ModelField) -> NormalizedModelField:
        types, is_list = self.normalize_type(field.type_)

        return NormalizedModelField(
            field=field,
            types=types,
            is_list=is_list,
        )

