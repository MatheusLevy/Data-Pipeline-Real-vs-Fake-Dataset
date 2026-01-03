from filters.filter_base import Filter
from models.config import Source

class FilterFactory():
    @staticmethod
    def get_filter(filter_name: str, config: Source) -> Filter:
        if filter_name == 'flatten':
            from filters.flatten_dataset import FlattenDataset
            return FlattenDataset(config)
        if filter_name == 'extract':
            from filters.extract import Extract
            return Extract(config)
        if filter_name == 'exclude_subfolder':
            from filters.exclude_subfolder import ExcludeSubFolder
            return ExcludeSubFolder(config)
        if filter_name == 'exclude_low_quality':
            from filters.exclude_low_quality import ExcludeLowQuality
            return ExcludeLowQuality(config)
        raise ValueError(f"Unknown filter: {filter_name}")