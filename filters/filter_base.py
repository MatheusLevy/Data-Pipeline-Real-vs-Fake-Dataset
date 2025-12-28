from abc import ABC, abstractmethod
import logging


class Filter(ABC):
    def __init__(self, config: dict) -> None:
        self.config = config
        self.logger = logging.getLogger(f"pipeline.filter.{self.__class__.__name__}")

    @abstractmethod
    def apply(self, images: list) -> list:
        pass