# app/api/routes/media.py
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import uuid4

from app.core.security import get_current_user
from app.services.media import create_presigned_url
from app.schemas.media import PresignedURLResponse

router = APIRouter()


@router.post("/presign", response_model=PresignedURLResponse)
async def get_presigned_url(
    content_type: str = Query(..., description="MIME type of the file (e.g. image/png, video/mp4)"),
    current_user=Depends(get_current_user),
):
    """
    Generate a presigned S3 URL for uploading a file.
    Only allows image/* and video/* content types.
    """
    if not content_type.startswith(("image/", "video/")):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    key = f"user_uploads/{current_user.id}/{uuid4()}"
    url = create_presigned_url(key, content_type)

    return PresignedURLResponse(upload_url=url, object_key=key)
