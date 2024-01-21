from typing import Any, Optional


class ReferenceRegister:
    def __init__(self, *, base_data: Optional[dict] = None) -> None:
        self._data = base_data or {}

    def bind(self, f):
        for k, v in self._data.items():
            setattr(k, v, f)

    def __call__(self, referencer: Any, _getter_name: str) -> Any:
        self._data[referencer] = _getter_name
        return referencer

