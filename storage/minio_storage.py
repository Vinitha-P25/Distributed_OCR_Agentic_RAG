import logging
import os
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from minio import Minio

load_dotenv()

logger = logging.getLogger(__name__)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "documents")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"


def get_minio_client() -> Minio:
    """Create a MinIO client using environment configuration."""

    if not MINIO_ACCESS_KEY or not MINIO_SECRET_KEY:
        raise RuntimeError(
            "MINIO_ACCESS_KEY and MINIO_SECRET_KEY "
            "must be configured in the .env file."
        )

    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
    )


def ensure_bucket_exists() -> None:
    """Create the configured bucket if it does not exist."""

    client = get_minio_client()

    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)
        logger.info("Created MinIO bucket: %s", MINIO_BUCKET)
    else:
        logger.info("MinIO bucket already exists: %s", MINIO_BUCKET)


def upload_bytes(
    content: bytes,
    object_name: str,
    content_type: str = "application/pdf",
) -> str:
    """Upload file bytes to MinIO and return the object key."""

    if not content:
        raise ValueError("Cannot upload an empty file.")

    client = get_minio_client()
    ensure_bucket_exists()

    client.put_object(
        bucket_name=MINIO_BUCKET,
        object_name=object_name,
        data=BytesIO(content),
        length=len(content),
        content_type=content_type,
    )

    logger.info("Uploaded object to MinIO: %s", object_name)

    return object_name


def download_object(
    object_name: str,
    destination_path: str | Path,
) -> Path:
    """Download an object from MinIO to a local file."""

    client = get_minio_client()

    destination = Path(destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    client.fget_object(
        bucket_name=MINIO_BUCKET,
        object_name=object_name,
        file_path=str(destination),
    )

    logger.info("Downloaded MinIO object: %s", object_name)

    return destination


def object_exists(object_name: str) -> bool:
    """Check whether an object exists in the configured bucket."""

    from minio.error import S3Error

    client = get_minio_client()

    try:
        client.stat_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_name,
        )
        return True

    except S3Error as exc:
        if exc.code in ("NoSuchKey", "NoSuchObject", "NotFound"):
            return False
        raise