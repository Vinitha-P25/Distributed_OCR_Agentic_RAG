import os

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config


S3_ENDPOINT_URL = os.getenv(
    "S3_ENDPOINT_URL",
    "http://localhost:8333",
)

S3_ACCESS_KEY = os.getenv(
    "S3_ACCESS_KEY",
    "ocr_access_key",
)

S3_SECRET_KEY = os.getenv(
    "S3_SECRET_KEY",
    "ocr_secret_key",
)

S3_BUCKET_NAME = os.getenv(
    "S3_BUCKET_NAME",
    "ocr-documents",
)


s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT_URL,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name="us-east-1",
    config=Config(signature_version="s3v4"),
)


def create_bucket():
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        print(f"Bucket '{S3_BUCKET_NAME}' already exists.")
        return S3_BUCKET_NAME

    except ClientError as error:
        error_code = error.response.get("Error", {}).get("Code", "")

        if error_code not in ("404", "NoSuchBucket", "NotFound"):
            if error_code in ("403", "AccessDenied"):
                raise RuntimeError(
                    f"Cannot access bucket '{S3_BUCKET_NAME}'. "
                    "Check the object-storage credentials and permissions."
                ) from error

            raise

    try:
        s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
        print(f"Bucket '{S3_BUCKET_NAME}' created successfully.")

    except ClientError as error:
        error_code = error.response.get("Error", {}).get("Code", "")

        if error_code not in (
            "BucketAlreadyOwnedByYou",
            "BucketAlreadyExists",
        ):
            raise

        print(f"Bucket '{S3_BUCKET_NAME}' already exists.")

    return S3_BUCKET_NAME

def upload_file(file_path: str, object_name: str) -> dict:
    """
    Upload a local file to SeaweedFS object storage.
    """
    bucket_name = create_bucket()

    s3_client.upload_file(
        file_path,
        bucket_name,
        object_name,
    )

    return {
        "bucket": bucket_name,
        "object_name": object_name,
    }


def download_file(object_name: str, destination_path: str) -> str:
    """
    Download a file from SeaweedFS object storage.
    """
    create_bucket()

    s3_client.download_file(
        S3_BUCKET_NAME,
        object_name,
        destination_path,
    )

    return destination_path


def delete_file(object_name: str) -> None:
    """
    Delete a file from SeaweedFS object storage.
    """
    s3_client.delete_object(
        Bucket=S3_BUCKET_NAME,
        Key=object_name,
    )