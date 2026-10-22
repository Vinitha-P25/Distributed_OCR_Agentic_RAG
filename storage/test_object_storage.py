import boto3
from botocore.config import Config

S3_ENDPOINT_URL = "http://localhost:8333"
S3_ACCESS_KEY = "ocr_access_key"
S3_SECRET_KEY = "ocr_secret_key"
BUCKET_NAME = "ocr-documents"

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT_URL,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name="us-east-1",
    config=Config(signature_version="s3v4"),
)

try:
    response = s3.list_buckets()
    print("S3 connection successful.")
    print("Existing buckets:", response.get("Buckets", []))

    if not any(
        bucket["Name"] == BUCKET_NAME
        for bucket in response.get("Buckets", [])
    ):
        s3.create_bucket(Bucket=BUCKET_NAME)
        print(f"Created bucket: {BUCKET_NAME}")
    else:
        print(f"Bucket already exists: {BUCKET_NAME}")

except Exception as error:
    print("S3 test failed:", error)