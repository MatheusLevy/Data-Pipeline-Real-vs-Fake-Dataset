from pyparsing import ABC, abstractmethod


class Filter(ABC):
    
    def __init__(self, config: dict) -> None:
        self.config = config
    
    @abstractmethod
    def apply(self, images: list[str]) -> list[str]:
        pass