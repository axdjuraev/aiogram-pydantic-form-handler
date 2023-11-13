

from typing import Optional


class FieldMetadata:
    def __init__(
        self, 
        type: str,
        view_text: Optional[str] = None,
        getter_name: Optional[str] = None,
    ) -> None:
        self._type = type
        self._view_text = view_text
        self._getter_name = getter_name

