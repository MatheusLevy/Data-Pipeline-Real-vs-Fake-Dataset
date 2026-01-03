import os
from pathlib import Path
from typing import Tuple
from models.metadata import BronzeMetadata, Metadata
from sources.base_handler import BaseHandler
from roboflow import Roboflow
from roboflow.core.project import Project
from roboflow.core.version import Version
from dotenv import load_dotenv
import re
from utils.stout import _suppress_output
load_dotenv()

class RoboflowHandler(BaseHandler):

    def __init__(self, source_name, config):
        super().__init__(source_name, config)
        with _suppress_output():
            self.rf = Roboflow(api_key=os.getenv("API_KEY_ROBOFLOW"))
    
    def _get_workspace(self) -> str:
        url: str = self.config.url
        workspace_name: str = url.split("/")[-2]
        return workspace_name

    def _get_project_id(self) -> str:
        url: str = self.config.url
        project_id: str = url.split("/")[-1]
        return project_id
    
    def _get_path_of_images(self, directory: Path) -> list[Path]:
        return [
            p for p in directory.rglob("*")
            if p.is_file() and re.search(r"\.(jpe?g|png)$", p.name, re.IGNORECASE)
        ]
    
    def _dowload_from_roboflow(self, workspace: str, project_id: str) -> list[Path]:
        project: Project = self.rf.workspace(workspace).project(project_id=project_id)
        version: Version = project.version(self.config.version)
        bronze_path: Path = Path(os.path.join(os.getenv("BRONZE_DIR", "./bronze"), f"{self.config.id}"))
        version.download("yolov12", location=str(bronze_path))
        return self._get_path_of_images(bronze_path)

    def download_images(self) -> Tuple[list[Path], Metadata]:
        workspace: str = self._get_workspace()
        project_id: str = self._get_project_id()
        with _suppress_output():
            images: list[Path] = self._dowload_from_roboflow(workspace, project_id)
        metadata: Metadata = self._build_metadata()
        return images, metadata
    
    def save_metadata(self, metadata: Metadata):
        super().save_metadata(metadata)
    