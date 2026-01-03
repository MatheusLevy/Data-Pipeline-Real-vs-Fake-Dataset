import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

class CheckpointManager:
    def __init__(self, checkpoint_dir: str = ".checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
    
    def _get_checkpoint_path(self, source_id: str) -> Path:
        return self.checkpoint_dir / f"{source_id}.json"
    
    def save_checkpoint(self, source_id: str, stage: str, data: dict) -> None:
        checkpoint = {
            "source_id": source_id,
            "stage": stage,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        with open(self._get_checkpoint_path(source_id), 'w') as f:
            json.dump(checkpoint, f, indent=2)
    
    def load_checkpoint(self, source_id: str) -> Optional[dict]:
        path = self._get_checkpoint_path(source_id)
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return None
    
    def clear_checkpoint(self, source_id: str) -> None:
        path = self._get_checkpoint_path(source_id)
        if path.exists():
            path.unlink()
    
    def should_skip_stage(self, source_id: str, stage: str) -> bool:
        checkpoint = self.load_checkpoint(source_id)
        if checkpoint and checkpoint.get("stage") == stage:
            return True
        return False
