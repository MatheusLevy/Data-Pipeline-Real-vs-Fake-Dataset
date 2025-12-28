class FilterFactory():
    @staticmethod
    def get_filter(filter_name: str, config: dict):
        if filter_name == 'flatten':
            from filters.flatten_dataset import FlattenDataset
            return FlattenDataset(config)
        if filter_name == 'extract':
            from filters.extract import Extract
            return Extract(config)
        raise ValueError(f"Unknown filter: {filter_name}")