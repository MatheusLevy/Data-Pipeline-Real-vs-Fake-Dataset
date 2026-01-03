from pathlib import Path
from typing import List, Tuple
from models.config import Source
from models.metadata import BronzeMetadata, Metadata
from sources.base_handler import BaseHandler
import requests
import os

class KaggleHandler(BaseHandler):
    def __init__(self, source_name: str, config: Source):
        super().__init__(source_name, config)

    def _download_zip(self, url: str) -> Path:
        response: requests.Response = requests.get(url, allow_redirects=True, stream=True)
        response.raise_for_status()
        zip_dir: str = os.path.join(os.getenv("BRONZE_DIR", "./bronze"), self.config.id)
        os.makedirs(zip_dir, exist_ok=True)
        zip_path: str = os.path.join(zip_dir, "dataset.zip")
        self._save_data_stream(response, zip_path)
        return Path(zip_path)
    
    def download_images(self) -> Tuple[List[Path], Metadata]:
        dataset_id: str = self._get_dataset_name()
        url: str = "https://www.kaggle.com/api/v1/datasets/download/" + dataset_id
        zip_path: Path = self._download_zip(url)
        bronze_metadata: Metadata = self._build_metadata("bronze")
        return [zip_path], bronze_metadata

    def _save_data_stream(self, response: requests.Response, dest_path: str) -> None:
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    def _get_dataset_name(self) -> str:
        """Helper method to get a Kaggle dataset id (owner/dataset)"""
        url: str = self.config.url
        parts = url.rstrip('/').split('/')
        dataset_id: str = f"{parts[-2]}/{parts[-1]}"
        return dataset_id
    
    def save_metadata(self, metadata: Metadata):
        super().save_metadata(metadata)