from pathlib import Path
from filters.filter_base import Filter

class ExcludeSubFolder(Filter):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.subfolders_name = config.get('filters_params', {}).get('exclude_subfolder', {}).get('subfolders', [])
        print("ExcludeSubFolder subfolders_name:", self.subfolders_name)
        if not self.subfolders_name:
            self.logger.warning('ExcludeSubFolder initialized without a subfolders name; it will no-op')
        else:
            self.logger.info(f"ExcludeSubFolder initialized for '{self.subfolders_name}'")
        
    def apply(self, images: list) -> list:
        if not self.subfolders_name:
            return images
        self.logger.info(f"ExcludeSubFolder: excluding subfolders {self.subfolders_name}")
        filtered_images = [
            img for img in images if not any(subfolder in Path(str(img)).parts for subfolder in self.subfolders_name)
        ]
        self.logger.info(f"ExcludeSubFolder: excluded {len(images) - len(filtered_images)} images")
        return filtered_images