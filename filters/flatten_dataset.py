from filters.filter_base import Filter
from pathlib import Path

class FlattenDataset(Filter):
    def apply(self, image_paths: list) -> list:
        self.logger.info("FlattenDataset filter: starting")
        flattened_paths: list[str] = []
        for path in image_paths:
            path = Path(path)
            if path.is_dir():
                for sub_path in path.rglob('*'):
                    if sub_path.is_file():
                        flattened_paths.append(str(sub_path))
            else:
                flattened_paths.append(str(path))
        self.logger.info(f"FlattenDataset filter: finished ({len(flattened_paths)} paths)")
        return flattened_paths