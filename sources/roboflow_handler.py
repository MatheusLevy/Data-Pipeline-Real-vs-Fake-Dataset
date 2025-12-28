import os
from pathlib import Path
from sources.base_handler import BaseHandler
from roboflow import Roboflow
from roboflow.core.project import Project
from roboflow.core.version import Version
from dotenv import load_dotenv
import re
load_dotenv()

class RoboflowHandler(BaseHandler):

    def __init__(self, source_name, config):
        super().__init__(source_name, config)
        self.rf = Roboflow(api_key=os.getenv("API_KEY_ROBOFLOW"))

    def extract(self, filters):
        """Extract raw data from Roboflow"""
        self.logger.info("Extracting data from Roboflow")
        pass
    
    def _get_workspace(self) -> str:
        """Helper method to get a Roboflow workspace"""
        url: str = self.config.get("url")
        workspace_name: str = url.split("/")[-2]
        return workspace_name

    def _get_project_id(self) -> str:
        """Helper method to get a Roboflow dataset name"""
        url: str = self.config.get("url")
        project_id: str = url.split("/")[-1]
        return project_id
    
    def filter(self, raw_data, filters):
        """Apply Roboflow-specific filters"""
        self.logger.info("Filtering Roboflow data")
        # Implementation for filtering Roboflow data
        pass
    
    def download_images(self) -> list[Path]:
        """Download the selected images from Roboflow"""
        self.logger.info("Downloading images from Roboflow")
        workspace: str = self._get_workspace()
        project_id: str = self._get_project_id()
        project: Project = self.rf.workspace(workspace).project(project_id=project_id)
        version: Version = project.version(self.config.get("version", 1))
        temp_path = f"temp/roboflow-{project_id}"
        version.download("yolov12", location=temp_path)
        image_paths = [
            p for p in Path(temp_path).rglob("*")
            if re.search(r"\.(jpe?g|png)$", p.suffix, re.IGNORECASE)
        ]
        return image_paths
    
    def save_metadata(self, images):
        """Save metadata for the downloaded Roboflow images"""
        self.logger.info("Saving metadata for Roboflow images")
        # Implementation for saving metadata
        pass
    