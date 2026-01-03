from pathlib import Path
from filters.filter_base import Filter
import cv2
import numpy as np
from models.config import Source

class ExcludeLowQuality(Filter):
    def __init__(self, config: Source) -> None:
        super().__init__(config)

    def _has_min_size(self, image: np.ndarray) -> bool:
        min_height: int = self.config.filters_params["exclude_low_quality"]["min_height"]
        min_width: int = self.config.filters_params["exclude_low_quality"]["min_width"]
        height, width = image.shape
        return height >= min_height and width >= min_width
    
    def _has_min_contrast(self, image: np.ndarray) -> bool:
        contrast = image.std()
        min_contrast: int = self.config.filters_params["exclude_low_quality"]["min_contrast"]
        return contrast >= min_contrast

    def _has_min_laplacian_sharpness(self, image: np.ndarray) -> bool:
        laplacian = cv2.Laplacian(image, cv2.CV_64F)
        variance = laplacian.var()
        min_laplacian_sharpness: int = self.config.filters_params["exclude_low_quality"]["min_laplacian_sharpness"]
        return variance >= min_laplacian_sharpness
    
    def _is_corruped(self, image: np.ndarray) -> bool:
        return image is None
    
    def apply(self, images: list[Path]) -> list[Path]:
        filtered_images: list[Path] = []
        for image_path in images:
            image: np.ndarray = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE) 
            if self._is_corruped(image):
                continue
            if not self._has_min_size(image) or not self._has_min_contrast(image) or not self._has_min_laplacian_sharpness(image):
                continue
            filtered_images.append(image_path)
        return filtered_images