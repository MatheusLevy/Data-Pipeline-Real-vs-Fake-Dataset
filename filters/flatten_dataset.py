from filters.filter_base import Filter

class FlattenDataset(Filter):
    def apply(self, image_paths: list[str]) -> list[str]:
        """Flatten nested directories into a single list of image paths"""
        flattened_paths: list[str] = []
        for path in image_paths:
            print(path)
            if path.is_dir():
                for sub_path in path.rglob('*'):
                    if sub_path.is_file():
                        flattened_paths.append(sub_path)
            else:
                flattened_paths.append(path)
        return flattened_paths