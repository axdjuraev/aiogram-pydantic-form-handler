from typing import Iterable
from pydantic.fields import ModelField


__all__ = [
    'get_step_name',
]


def get_step_name(field: ModelField, parents: Iterable[str]):
    if len(tuple(parents)) < 2:
        return f"{field.name}"

    return f'{"".join(tuple(parents)[1:])}_{field.name}'

