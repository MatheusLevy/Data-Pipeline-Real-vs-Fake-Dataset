import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

@dataclass
class SourceMetrics:
    source_id: str
    source_name: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = None
    images_downloaded: int = 0
    images_after_filters: int = 0
    images_to_silver: int = 0
    filters_applied: Dict[str, dict] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def record_filter(self, filter_name: str, before: int, after: int):
        self.filters_applied[filter_name] = {
            "before": before,
            "after": after,
            "removed": before - after
        }
    
    def finish(self):
        self.end_time = datetime.now()
    
    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0

@dataclass  
class PipelineReport:
    run_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    sources_metrics: List[SourceMetrics] = field(default_factory=list)
    
    def add_source_metrics(self, metrics: SourceMetrics):
        self.sources_metrics.append(metrics)
    
    def save(self, output_dir: str = "./reports"):
        os.makedirs(output_dir, exist_ok=True)
        report_path = Path(output_dir) / f"pipeline_report_{self.run_id}.json"
        
        report_data = {
            "run_id": self.run_id,
            "total_sources": len(self.sources_metrics),
            "total_images_processed": sum(m.images_to_silver for m in self.sources_metrics),
            "total_duration_seconds": sum(m.duration_seconds for m in self.sources_metrics),
            "sources": [asdict(m) for m in self.sources_metrics]
        }
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return report_path