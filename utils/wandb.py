import logging
from pathlib import Path
from models.report import PipelineReport
from utils.git import get_current_commit_hash
import wandb
import os
from datetime import datetime
import dotenv
dotenv.load_dotenv()
import json

LOG_LEVEL = os.getenv("PIPELINE_LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("pipeline.orchestrator")

def read_pipeline_report(report_path: str) -> dict:
    with open(report_path, 'r') as file:
        report = json.load(file)
    return report

def save_report(report: PipelineReport) -> Path:
    """Save pipeline report to disk"""
    report_path: Path = report.save()
    logger.info(f"Pipeline report saved to: {report_path}")
    return report_path

def save_dataset_version(project_name: str, dataset_name: str, report: PipelineReport):
    with wandb.init(project=project_name) as run:
        report.add_wandb_run_name(run.name)
        save_report(report)
        artifact = wandb.Artifact(
            name=dataset_name, 
            type="dataset",
            description="Dataset versionion of Natural vs Unnatural Images Classification tracked in Weights & Biases and refered in s3 MinIO"
        )
        artifact.add_dir(
            local_path=os.getenv("BRONZE_DIR"),
            name="bronze"
        )
        artifact.add_dir(
            local_path=os.getenv("SILVER_DIR"),
            name="silver"
        )
        artifact.metadata = {
            "bronze_bucket": os.getenv("BRONZE_BUCKET_NAME"),
            "bronze_folder_path": os.getenv("BRONZE_FOLDER_PATH"),
            "silver_bucket": os.getenv("SILVER_BUCKET_NAME"),   
            "silver_folder_path": os.getenv("SILVER_FOLDER_PATH"),
            "tracked_by": "Weights & Biases",
            "folder structure": {
                "bronze": "Raw ingested data",
                "silver": "Processed and cleaned data ready for model training"
            },
            "pipeline_version": get_current_commit_hash(),
            "created_by": "Data Pipeline for Natural vs Unnatural Images Classification",
            "creation_date": datetime.now().isoformat(),
            "report": read_pipeline_report("silver/metadata/pipeline_report.json")
        }

        run.log_artifact(artifact)
        print(f"Dataset version '{dataset_name}' saved to Weights & Biases project '{project_name}'")
        
    