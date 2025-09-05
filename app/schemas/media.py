from pydantic import BaseModel, Field


class PresignedURLResponse(BaseModel):
    """Response schema for presigned S3 upload URL."""
    upload_url: str = Field(..., description="The presigned S3 URL to upload the file")
    object_key: str = Field(..., description="The S3 object key where the file will be stored")
