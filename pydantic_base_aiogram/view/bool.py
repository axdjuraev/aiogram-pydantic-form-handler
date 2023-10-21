from typing import Optional

from .base import BaseView 


class BoolView(BaseView):
    @property
    def view_text_format(self):
        return self.dialects.CHOOSE_FROM_LIST

    @property
    def extra_keys(self) -> Optional[dict[str, str]]:
        keys = {}
        
        if self._extra_keys:
            self._extra_keys.update(self._extra_keys)

        keys[f"{self.item_callback_data}:1"] = self.dialects.BOOL_CHOICE_YES
        keys[f"{self.item_callback_data}:0"] = self.dialects.BOOL_CHOICE_NO

        return keys

