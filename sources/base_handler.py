from abc import ABC, abstractmethod
import logging

class BaseHandler(ABC):
    def __init__(self, source_name, config):
        self.source_name = source_name
        self.config = config
        self.logger = logging.getLogger(f"pipeline.{source_name}")
        
    @abstractmethod
    def extract(self, filters):
        """Extract raw data from the source"""
        pass
    
    @abstractmethod
    def filter(self, raw_data, filters):
        """Apply source-specific filters"""
        pass
    
    @abstractmethod
    def download_images(self):
        """Download the selected images"""
        pass
    
    def save_metadata(self, images):
        """Save metadata for the downloaded images"""
        pass

    def run(self, filters):
        """Template method — standard flow"""
        self.logger.info(f"Starting extraction for {self.source_name}")
        
        raw_data = self.extract(filters)
        filtered = self.filter(raw_data, filters)
        images = self.download_images()
        self.save_metadata(images)
        
        return images