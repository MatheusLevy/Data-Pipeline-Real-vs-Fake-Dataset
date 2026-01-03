from pathlib import Path
from PIL import Image
import os
import warnings
from utils.stout import _suppress_output

def image_info(image_path: Path) -> dict:
    """Extract metadata from image file"""
    try:
        warnings.filterwarnings('ignore', category=UserWarning, module='PIL')
        with _suppress_output():
            with Image.open(image_path) as img:
                width, height = img.size
    except ImportError:
        width, height = None, None
    stats: os.stat_result = image_path.stat()
    metadata = {
        "size_bytes": stats.st_size,
        "source_image_name": image_path.name,
        "source_image_path": str(image_path.relative_to(os.getenv("BRONZE_DIR", "./bronze"))),
        "height": height,
        "width": width,
        "format": image_path.suffix.replace('.', '').upper(),
    }
    return metadata