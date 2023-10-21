
class DataValidationError(Exception):
    def __init__(self, detail: str, *args: object) -> None:
        super().__init__(*args)
        self.detail = detail

