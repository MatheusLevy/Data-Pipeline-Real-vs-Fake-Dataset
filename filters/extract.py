from filters.filter_base import Filter
import zipfile
import os

class Extract(Filter):
    def apply(self, images: list[str]) -> list[str]:
        zip_paths = [img for img in images if img.endswith('.zip')]
        extracted_paths: list[str] = []
        for zip_path in zip_paths:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                extract_dir = zip_path.rstrip('.zip')
                os.makedirs(extract_dir, exist_ok=True)
                zip_ref.extractall(extract_dir)
                for root, _, files in os.walk(extract_dir):
                    for file in files:
                        extracted_paths.append(os.path.join(root, file))
        return extracted_paths