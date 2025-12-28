from filters.filter_base import Filter
import zipfile
import os

class Extract(Filter):
    def apply(self, images: list) -> list:
        self.logger.info("Extract filter: starting")
        zip_paths = [str(img) for img in images if str(img).lower().endswith('.zip')]
        extracted_paths: list[str] = []
        for zip_path in zip_paths:
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    extract_dir = zip_path.rstrip('.zip')
                    os.makedirs(extract_dir, exist_ok=True)
                    zip_ref.extractall(extract_dir)
                    for root, _, files in os.walk(extract_dir):
                        for file in files:
                            extracted_paths.append(os.path.join(root, file))
                self.logger.info(f"Extract filter: extracted from {zip_path}")
            except Exception as e:
                self.logger.exception(f"Extract filter: failed to extract {zip_path}: {e}")
        self.logger.info(f"Extract filter: finished (found {len(extracted_paths)} files)")
        return extracted_paths