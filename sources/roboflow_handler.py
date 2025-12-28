import os
from pathlib import Path
from sources.base_handler import BaseHandler
from roboflow import Roboflow
from roboflow.core.project import Project
from roboflow.core.version import Version
from dotenv import load_dotenv
import re
from contextlib import contextmanager, redirect_stdout, redirect_stderr
import io
load_dotenv()

@contextmanager
def _suppress_output():
    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        yield

class RoboflowHandler(BaseHandler):

    def __init__(self, source_name, config):
        super().__init__(source_name, config)
        self.logger.info("Initializing Roboflow client (silencing library output)")
        with _suppress_output():
            self.rf = Roboflow(api_key=os.getenv("API_KEY_ROBOFLOW"))
    
    def _get_workspace(self) -> str:
        url: str = self.config.get("url")
        workspace_name: str = url.split("/")[-2]
        return workspace_name

    def _get_project_id(self) -> str:
        url: str = self.config.get("url")
        project_id: str = url.split("/")[-1]
        return project_id
    
    def download_images(self) -> list[Path]:
        self.logger.info("Downloading images from Roboflow")
        workspace: str = self._get_workspace()
        project_id: str = self._get_project_id()
        self.logger.debug(f"Workspace={workspace}, Project={project_id}, Version={self.config.get('version',1)}")
        temp_path = f"temp/roboflow-{project_id}"
        self.logger.info(f"Downloading version to {temp_path} (Roboflow output suppressed)")
        with _suppress_output():
            project: Project = self.rf.workspace(workspace).project(project_id=project_id)
            version: Version = project.version(self.config.get("version", 1))
            version.download("yolov12", location=temp_path)
        image_paths = [
            p for p in Path(temp_path).rglob("*")
            if p.is_file() and re.search(r"\.(jpe?g|png)$", p.name, re.IGNORECASE)
        ]
        self.logger.info(f"Roboflow: found {len(image_paths)} image files")
        return image_paths
    
    def save_metadata(self, images):
        self.logger.info("Saving metadata for Roboflow images")
        # Implementation for saving metadata
        pass
    