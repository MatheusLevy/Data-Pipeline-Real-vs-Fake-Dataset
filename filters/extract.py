from pathlib import Path
from filters.filter_base import Filter
import zipfile
import os
import re

class Extract(Filter):

    def _extract_zip(self, zip_path: str, extract_to: str) -> list[Path]:
        extracted_files: list[Path] = []
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
                for root, _, files in os.walk(extract_to):
                    for file in files:
                        # Only include image files
                        if re.search(r"\.(jpe?g|png|bmp|gif|tiff?)$", file, re.IGNORECASE):
                            extracted_files.append(Path(os.path.join(root, file)))
        except Exception as e:
            self.logger.exception(f"Extract filter: failed to extract {zip_path}: {e}")
        finally:
            os.remove(zip_path)
        return extracted_files
    
    def apply(self, images: list[Path]) -> list[Path]:
        self.logger.info("Extract filter: starting")
        zip_paths = [str(img) for img in images if str(img).lower().endswith('.zip')]
        extracted_paths: list[Path] = []
        for zip_path in zip_paths:
            extracted_files: list[Path] = self._extract_zip(zip_path, os.path.dirname(zip_path))
            extracted_paths.extend(extracted_files)
        return extracted_paths