from uuid import uuid4
from pydantic import BaseModel, Field
from typing import Any, Any, Dict, Dict, List, List, Optional
from datetime import datetime

class Metadata(BaseModel):
    name: Optional[str] = None
    id: Optional[str] = None

    def model_post_init(self, __context):
        if self.id is None and self.name is not None:
            self.id = self.name.lower().replace(" ", "_")

class BronzeMetadata(Metadata):
    author: str
    type: str
    source: str
    handler: str
    url: str
    license: Optional[str] = None
    date: str
    version: Optional[int] = None
    model: Optional[str] = None
    creation_date: str = datetime.now().isoformat()

class SilverMetadata(Metadata):
    source_image_name: Optional[str] = None
    source_image_path: Optional[str] = None
    source_id: Optional[str] = None
    source_name: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    size_bytes: Optional[int] = None
    processed_date: str = datetime.now().isoformat()
    filters: List[str] = Field(default_factory=list)
    filters_params: Dict[str, Dict[str, Any]] = Field(default_factory=dict)