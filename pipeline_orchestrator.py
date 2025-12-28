import os
import logging
import yaml
from sources.base_handler import BaseHandler
from sources.handler_factory import HandlerFactory
import shutil
import hashlib
from pathlib import Path

LOG_LEVEL = os.getenv("PIPELINE_LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

class ImagePipelineOrchestrator:
    def __init__(self, config_path='configs/sources.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def run_pipeline(self, sources=None):
        """Run the pipeline for the specified sources"""
        sources: list[dict] = self.config.get('sources', [])
        for source_cfg in sources:
            handler: BaseHandler = HandlerFactory.get_handler(source_cfg['handler'], source_cfg)
            images_path: list[Path] = handler.run()
            self.consolidate_images(images_path)
        shutil.rmtree('temp', ignore_errors=True)
        
    def _sha256_of_file(self, path) -> str:
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    
    def consolidate_images(self, image_paths: list[Path]) -> None:
        """Copy images into a single output directory, naming files by their SHA-256 hash"""
        output_dir = Path('images')
        output_dir.mkdir(exist_ok=True)

        for img_path in image_paths:
            img_path = Path(img_path)
            file_hash = self._sha256_of_file(img_path)
            new_name = f"{file_hash}{img_path.suffix}"
            dest = output_dir / new_name
            if not dest.exists():
                shutil.copy(img_path, dest)

if __name__ == "__main__":
    orchestrator = ImagePipelineOrchestrator()
    orchestrator.run_pipeline()