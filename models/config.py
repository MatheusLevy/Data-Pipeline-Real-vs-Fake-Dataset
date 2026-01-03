from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
import yaml
import os

class Remote(BaseModel):
    type: str
    bucket_name: str
    path: Optional[str] = None
    profile: Optional[str] = None

class Source(BaseModel):
    id: Optional[str] = None
    name: str
    author: str
    type: str
    source: str
    handler: str
    url: str
    license: Optional[str] = None
    date: str
    current_date: Optional[datetime] = Field(default_factory=datetime.now)
    version: int = Field(default=1)
    model: Optional[str] = None
    filters: List[str] = Field(default_factory=list)
    filters_params: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str, info) -> str:
        if info.data.get('handler') == 'roboflow' and 'roboflow.com' not in v:
            raise ValueError('Roboflow handler requires roboflow.com URL')
        if info.data.get('handler') == 'kaggle' and 'kaggle.com' not in v:
            raise ValueError('Kaggle handler requires kaggle.com URL')
        return v
    
    @model_validator(mode='after')
    def validate_filters_params(self):
        for filter_name in self.filters:
            if filter_name in ['exclude_low_quality', 'exclude_subfolder']:
                if filter_name not in self.filters_params:
                    raise ValueError(f"Filter '{filter_name}' requires params in filters_params")
        return self
    
    def model_post_init(self, __context):
        if self.id is None:
            self.id = self.name.lower().replace(" ", "_")
    
class Config(BaseModel):
    sources: List[Source] = Field(default_factory=list)
    remote: Optional[Remote] = None

def load_config_from_dict() -> Config:
    config_path: str = os.getenv('CONFIG_PATH', 'configs/sources.yaml')
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
        return Config(**config_dict)