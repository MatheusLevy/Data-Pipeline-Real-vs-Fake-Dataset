from pathlib import Path
from models.config import Config, load_config_from_dict

CONFIG: Config = load_config_from_dict()
SOURCES_TEMP_FOLDERS: dict[str, Path] = {}

