from abc import ABC, abstractmethod
import logging
from pathlib import Path
import shutil
from typing import List, Optional, Tuple
from filters.filter_base import Filter
from filters.filter_factory import FilterFactory
import json
import os
from models.config import Source
from models.metadata import BronzeMetadata, Metadata, SilverMetadata
from models.report import SourceMetrics
from utils.checkpoint import CheckpointManager
from utils.hash import sha256_of_file
from utils.image import image_info

class BaseHandler(ABC):
    def __init__(self, source_name: str, config: Source):
        self.source_name = source_name
        self.config = config
        self.logger = logging.getLogger(f"pipeline.{source_name}")
        self.metrics = SourceMetrics(source_id=config.id, source_name=source_name)
        self.checkpoint_mgr = CheckpointManager()

    def _build_silver_metadata(self, image: Path) -> SilverMetadata:
        metadata: dict = self.config.model_dump()
        image_info_data: dict = image_info(image)
        hash_image: str = sha256_of_file(str(image))
        metadata.update({
            **image_info_data,
            "name": hash_image + image.suffix,
            "id": hash_image,
            "source_id": self.config.id,
            "source_name": self.source_name})
        return SilverMetadata(**metadata)
    
    def _build_metadata(self, layer: str = "bronze", image_path: Optional[Path] = None) -> Metadata:
        if layer == "bronze":
            metadata = BronzeMetadata(**self.config.model_dump())
            return metadata
        metadata = self._build_silver_metadata(image=image_path)
        return metadata
    

    def filter(self, images: list[Path]) -> Tuple[list[Path], List[SilverMetadata]]:
        filters: list[str] = self.config.filters
        filtered_images: list[Path] = images
        silver_metadata: list[SilverMetadata] = []
        for filter_name in filters:
            filter_handler: Filter = FilterFactory.get_filter(filter_name, self.config)
            count_before_filter = len(filtered_images) if filtered_images else 0
            filtered_images: list[Path] = filter_handler.apply(filtered_images)
            count_after_filter = len(filtered_images) if filtered_images else 0
            self.metrics.record_filter(filter_name, count_before_filter, count_after_filter)
            self.logger.info(f"Applied filter {filter_name}: {count_before_filter} -> {count_after_filter}")
        for image in filtered_images:
            silver_metadata.append(self._build_silver_metadata(image))
        self.metrics.images_after_filters = len(filtered_images)
        return filtered_images, silver_metadata
    
    @abstractmethod
    def download_images(self) -> Tuple[list[Path], Metadata]:
        """Download the selected images"""
        pass

    def get_metadata_dir(self, metadata: Metadata) -> str:
        if isinstance(metadata, BronzeMetadata):
            return os.getenv("BRONZE_DIR", "./bronze")
        else:
            return os.getenv("SILVER_DIR", "./silver")

    def save_metadata_bronze(self, metadata: BronzeMetadata) -> None:
        metadata_dir: str = self.get_metadata_dir(metadata)
        metadata_subfolder: str = os.getenv("METADATA_SUBFOLDER", "metadata")
        os.makedirs(f"{metadata_dir}/{metadata_subfolder}", exist_ok=True)
        with open(f"{metadata_dir}/{metadata_subfolder}/{metadata.id}.json", 'w') as f:
            json.dump(metadata.model_dump(), f, indent=4)

    def save_metadata_silver(self, metadata: List[SilverMetadata]) -> None:
        metadata_dir: str = self.get_metadata_dir(metadata)
        metadata_subfolder: str = os.getenv("METADATA_SUBFOLDER", "metadata")
        os.makedirs(f"{metadata_dir}/{metadata_subfolder}", exist_ok=True)
        for meta in metadata:
            with open(f"{metadata_dir}/{metadata_subfolder}/{meta.id}.json", 'w') as f:
                json.dump(meta.model_dump(), f, indent=4)
    
    def bronze(self) -> Tuple[list[Path], Metadata]:
        """Download images and save bronze metadata"""
        images, bronze_metadata = self.download_images()
        self.save_metadata_bronze(bronze_metadata)
        return images, bronze_metadata
    
    def copy_to_silver(self, metadata: List[SilverMetadata]) -> None:
        for meta in metadata:
            src_image_path = os.path.join(os.getenv("BRONZE_DIR", "./bronze"), meta.source_image_path)
            dest_image_path = Path(os.getenv("SILVER_DIR", "./silver")) / meta.name
            if not dest_image_path.exists():
                os.makedirs(dest_image_path.parent, exist_ok=True)
                shutil.copy2(src_image_path, dest_image_path)

    def _load_bronze_images(self) -> list[Path]:
        """Load existing images from the bronze layer"""
        bronze_dir = Path(os.getenv("BRONZE_DIR", "./bronze"))
        source_dir = bronze_dir / self.config.id
        
        if not source_dir.exists():
            self.logger.warning(f"Bronze directory not found: {source_dir}")
            return []
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
        images = []
        for ext in image_extensions:
            images.extend(source_dir.rglob(f"*{ext}"))
            images.extend(source_dir.rglob(f"*{ext.upper()}"))
        
        self.logger.info(f"Loaded {len(images)} images from bronze")
        return images

    def _should_skip_bronze(self) -> bool:
        """Check whether the bronze stage should be skipped"""
        return self.checkpoint_mgr.should_skip_stage(self.config.id, "bronze")

    def _execute_bronze(self) -> list[Path]:
        """Run the bronze stage or load existing images"""
        if not self._should_skip_bronze():
            self.logger.info("Starting bronze stage (download)")
            images, _ = self.bronze()
            self.checkpoint_mgr.save_checkpoint(
                self.config.id, "bronze",
                {"count": len(images), "timestamp": self.metrics.start_time.isoformat()}
            )
            self.logger.info(f"Bronze completed: {len(images)} images")
        else:
            self.logger.info("Skipping bronze (using checkpoint)")
            images = self._load_bronze_images()
        
        self.metrics.images_downloaded = len(images)
        return images

    def _execute_silver(self, images: list[Path]) -> None:
        """Execute silver stage (filters and copy)"""
        self.logger.info("Starting silver stage (filters)")
        images, silver_metadata = self.filter(images)
        self.save_metadata_silver(silver_metadata)
        self.copy_to_silver(silver_metadata)
        self.metrics.images_to_silver = len(silver_metadata)
        self.logger.info(f"Silver completed: {len(silver_metadata)} images")

    def _cleanup_checkpoint(self) -> None:
        """Remove checkpoint after successful run"""
        self.checkpoint_mgr.clear_checkpoint(self.config.id)

    def silver(self, images: list[Path]) -> None:
        """Filter images and save silver metadata"""
        images, silver_metadata = self.filter(images)
        self.save_metadata_silver(silver_metadata)
        self.copy_to_silver(silver_metadata)
        self.metrics.images_to_silver = len(silver_metadata)

    def run(self) -> SourceMetrics:
        try:
            images: List[Path] = self._execute_bronze()
            self._execute_silver(images)
            self._cleanup_checkpoint()
        except Exception as e:
            self.metrics.errors.append(str(e))
            self.logger.error(f"Pipeline error: {e}")
            raise
        finally:
            self.metrics.finish()
        return self.metrics