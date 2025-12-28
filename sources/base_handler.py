from abc import ABC, abstractmethod
import logging
from pathlib import Path
from filters.filter_base import Filter
from filters.filter_factory import FilterFactory

class BaseHandler(ABC):
    def __init__(self, source_name, config):
        self.source_name = source_name
        self.config = config
        self.logger = logging.getLogger(f"pipeline.{source_name}")
    
    def filter(self, images: list[Path]) -> list[Path]:
        """Apply Roboflow-specific filters"""
        self.logger.info("Filtering Roboflow data")
        pos_filters = self.config.get("pos-filters", [])
        for filter_name in pos_filters:
            filter: Filter = FilterFactory.get_filter(filter_name, self.logger)
            images = filter.apply(images)
        return images
    
    @abstractmethod
    def download_images(self) -> list[str]:
        """Download the selected images"""
        pass

    @abstractmethod
    def save_metadata(self, images):
        """Save metadata for the downloaded images"""
        pass

    def run(self):
        """Template method — standard flow"""
        self.logger.info(f"Starting extraction for {self.source_name}")
        images = self.download_images()
        images = self.filter(images)
        self.save_metadata(images)
        return images