from abc import ABC


class BasePydanticBaseAiogramException(Exception, ABC):
    pass


class DataValidationError(BasePydanticBaseAiogramException):
    def __init__(self, detail: str, *args: object) -> None:
        super().__init__(*args)
        self.detail = detail


class RequireMultipleError(BasePydanticBaseAiogramException):
    pass

