from pathlib import Path
import boto3
from botocore.client import Config
import os
import dotenv
dotenv.load_dotenv()

def _get_s3_client() -> boto3.client:
    session = boto3.Session(profile_name='minIO')
    return session.client(
        service_name='s3',
        endpoint_url=os.getenv("S3_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("MINIO_SECRET_KEY"),
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )

def upload_file_to_s3(file_path: Path, bucket_name: str, bucket_path: Path) -> None:
    s3_client: boto3.client = _get_s3_client()
    s3_client.upload_file(
            Filename=str(file_path),
            Bucket=bucket_name,
            Key=str(bucket_path / file_path.name)
    )

def upload_folder_to_s3(folder_path: Path, bucket_name: str, bucket_path: Path) -> None:
    s3_client: boto3.client = _get_s3_client()
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(folder_path)
            s3_client.upload_file(
                Filename=str(file_path),
                Bucket=bucket_name,
                Key=str(bucket_path / relative_path)
            )

def upload_to_silver_s3() -> None:
    silver_dir = Path(os.getenv("SILVER_DIR"))
    bucket_name = "classification-real-vs-fake"
    bucket_path = Path("silver")
    upload_folder_to_s3(silver_dir, bucket_name, bucket_path)