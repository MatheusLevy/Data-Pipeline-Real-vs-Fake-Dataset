from filters.filter_base import Filter
from pathlib import Path

class FlattenDataset(Filter):
    def apply(self, images: list[Path]) -> list[Path]:
        self.logger.info("FlattenDataset filter: starting")
        flattened_paths: list[Path] = []
        for path in images:
            path = Path(path)
            if path.is_dir():
                for sub_path in path.rglob('*'):
                    if sub_path.is_file():
                        flattened_paths.append(sub_path)
            else:
                flattened_paths.append(path)
        self.logger.info(f"FlattenDataset filter: finished ({len(flattened_paths)} paths)")
        return flattened_paths