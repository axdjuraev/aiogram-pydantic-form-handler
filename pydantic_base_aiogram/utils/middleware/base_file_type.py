from abc import ABC, abstractproperty


class BaseFileType(ABC):
    @abstractproperty
    def text_reprsentation(self) -> str:
        raise NotImplementedError
