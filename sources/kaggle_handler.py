from pathlib import Path
from sources.base_handler import BaseHandler
import requests
import os
import logging

class KaggleHandler(BaseHandler):
    def __init__(self, source_name, config):
        super().__init__(source_name, config)

    def download_images(self) -> list[Path]:
        self.logger.info("Downloading images from Kaggle")
        dataset_id: str = self._get_dataset_name()
        temp_path = f"temp/kaggle-{dataset_id.replace('/', '-') }"
        os.makedirs(temp_path, exist_ok=True)
        url: str = "https://www.kaggle.com/api/v1/datasets/download/" + dataset_id
        zip_path = None
        try:
            self.logger.debug(f"Kaggle download url: {url}")
            response = requests.get(url, allow_redirects=True, stream=True)
            response.raise_for_status()
            zip_path = os.path.join(temp_path, "dataset.zip")
            self._save_data_stream(response, zip_path)
            self.logger.info(f"Kaggle: saved dataset to {zip_path}")
            return [zip_path]
        except requests.HTTPError as e:
            self.logger.exception(f"Failed to download dataset from Kaggle: {e}")
            return []
        except Exception as e:
            self.logger.exception(f"Unexpected error downloading from Kaggle: {e}")
            return []

    def _save_data_stream(self, response: requests.Response, dest_path: str) -> None:
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    def _get_dataset_name(self) -> str:
        """Helper method to get a Kaggle dataset id (owner/dataset)"""
        url: str = self.config.get("url")
        parts = url.rstrip('/').split('/')
        dataset_id: str = f"{parts[-2]}/{parts[-1]}"
        return dataset_id
    
    def save_metadata(self, images):
        self.logger.info("Saving metadata for Kaggle images")
        # Implementation for saving metadata
        pass