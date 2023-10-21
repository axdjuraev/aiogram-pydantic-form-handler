from .enum.single import SingleValueEnumController


class BoolController(SingleValueEnumController):
    def _validate_data(self, data):
        return str(data).strip() == "1"

