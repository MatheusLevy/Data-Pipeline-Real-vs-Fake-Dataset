import logging
from pathlib import Path
from typing import AnyStr, Iterator, Tuple
import boto3
from botocore.client import Config
import os
import dotenv
from tqdm import tqdm

dotenv.load_dotenv()

LOG_LEVEL = os.getenv("PIPELINE_LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("pipeline.orchestrator")

def _get_s3_client() -> boto3.client:
    return boto3.client(
        service_name='s3',
        endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        config=Config(signature_version='s3v4'),
    )

def upload_file_to_s3(file_path: Path, bucket_name: str, bucket_path: Path) -> None:
    s3_client: boto3.client = _get_s3_client()
    s3_client.upload_file(
            Filename=str(file_path),
            Bucket=bucket_name,
            Key=str(bucket_path / file_path.name)
    )

def upload_folder_to_s3(folder_path: Path, bucket_name: str, bucket_path: Path) -> None:
    logger.info(f"Uploading contents of folder {folder_path} to s3://{bucket_name}/{bucket_path}/")
    total_files = sum(len(files) for _, _, files in os.walk(folder_path))
    s3_client: boto3.client = _get_s3_client()
    with tqdm(total=total_files, desc="Uploading files", unit="file") as progress_bar:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(folder_path)
                s3_client.upload_file(
                    Filename=str(file_path),
                    Bucket=bucket_name,
                    Key=str(bucket_path / relative_path)
                )
                progress_bar.update(1)
                progress_bar.set_postfix_str(str(relative_path))

def upload_to_label_studio_ingestion_silver_S3() -> None:
    silver_dir = Path(os.getenv("SILVER_DIR", "./silver"))
    bucket_name = os.getenv("LABEL_STUDIO_INGESTION_BUCKET", "classification-real-vs-fake")
    bucket_path = Path(os.getenv("BUCKET_PATH", "silver"))
    upload_folder_to_s3(silver_dir, bucket_name, bucket_path)