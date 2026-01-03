from abc import ABC, abstractmethod
import logging
from pathlib import Path
from models.config import Source


class Filter(ABC):
    def __init__(self, config: Source) -> None:
        self.config = config
        self.logger = logging.getLogger(f"pipeline.filter.{self.__class__.__name__}")

    @abstractmethod
    def apply(self, images: list[Path]) -> list[Path]:
        pass