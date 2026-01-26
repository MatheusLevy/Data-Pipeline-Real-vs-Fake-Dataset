import os
import logging
import yaml
from pathlib import Path
from models.config import Source
from models.report import PipelineReport, SourceMetrics
from sources.base_handler import BaseHandler
from sources.handler_factory import HandlerFactory
from utils.s3 import upload_to_label_studio_ingestion_silver_S3
from utils.wandb import save_dataset_version 
import dotenv
dotenv.load_dotenv()

LOG_LEVEL = os.getenv("PIPELINE_LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("pipeline.orchestrator")

def load_config() -> dict:
    """Load pipeline configuration from YAML file"""
    config_path = os.getenv("PIPELINE_CONFIG_PATH", "./configs/pipeline_config.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def create_handler(source_dict: dict) -> BaseHandler:
    """Create a handler instance for a source"""
    handler_type = source_dict['handler']
    source_cfg = Source(**source_dict)
    return HandlerFactory.get_handler(handler_type, source_cfg)

def process_source(source_dict: dict) -> SourceMetrics:
    """Process a single data source"""
    handler = create_handler(source_dict)
    return handler.run()

def process_all_sources(sources: list[dict]) -> PipelineReport:
    """Process all data sources and collect metrics"""
    report = PipelineReport()
    
    for source_dict in sources:
        source_name: str = source_dict.get('name', 'unknown')

        metrics: SourceMetrics = process_source(source_dict)
        report.add_source_metrics(metrics)
        logger.info(f"✓ {source_name}: {metrics.images_to_silver} images processed")

    
    return report

def main():
    """Main pipeline orchestrator"""
    config: dict = load_config()
    sources: list[dict] = config.get('sources', [])
    report: PipelineReport = process_all_sources(sources)
    save_dataset_version(project_name=os.getenv("PROJECT_NAME"), dataset_name=os.getenv("DATASET_NAME"), report=report)
    upload_to_label_studio_ingestion_silver_S3()
    
if __name__ == "__main__":
    main()