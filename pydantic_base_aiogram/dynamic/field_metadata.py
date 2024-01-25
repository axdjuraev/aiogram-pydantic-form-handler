from uuid import uuid4
from typing import Optional


class FieldMetadata:
    def __init__(
        self, 
        type: str,
        view_text: Optional[str] = None,
        field_name: Optional[str] = None,
        getter_name: Optional[str] = None,
        extra_keys: Optional[list[str]] = None,
        pre_next_method: Optional[str] = None,
    ) -> None:
        self._type = type
        self._view_text = view_text
        self._field_name = field_name or str(uuid4())
        self._getter_name = getter_name
        self._pre_next_method = pre_next_method
        self._extra_keys = dict(zip(extra_keys, extra_keys)) if extra_keys else None


