# app/services/media.py
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings


def create_presigned_url(key: str, content_type: str, expires_in: int = 3600) -> str:
    """
    Generate a presigned URL to upload a file to S3.
    """
    s3_client = boto3.client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )

    try:
        url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.aws_s3_bucket,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )
    except ClientError as e:
        raise RuntimeError(f"Error generating presigned URL: {e}")

    return url
 
