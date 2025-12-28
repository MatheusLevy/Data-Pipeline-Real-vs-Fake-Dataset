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
    
    def filter(self, images: list) -> list:
        self.logger.info("Applying post-filters")
        pos_filters = self.config.get("pos-filters", [])
        self.logger.debug(f"Post-filters configured: {pos_filters}")
        for filter_name in pos_filters:
            filter: Filter = FilterFactory.get_filter(filter_name, self.config)
            before = len(images) if images else 0
            images = filter.apply(images)
            after = len(images) if images else 0
            self.logger.info(f"Applied filter {filter_name}: {before} -> {after}")
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
        self.logger.info(f"Starting datapipeline for {self.source_name}")
        self.logger.debug("Downloading images...")
        images = self.download_images()
        self.logger.info(f"Downloaded {len(images)} items" if images else "No images downloaded")
        images = self.filter(images)
        self.logger.info("Saving metadata...")
        self.save_metadata(images)
        self.logger.info("Pipeline finished")
        return images