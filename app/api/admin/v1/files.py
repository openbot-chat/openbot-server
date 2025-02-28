from fastapi import APIRouter, Body
from models.api import UploadLinkRequest, UploadLinkResponse
from models.credentials import CredentialsSchemaBase
from core.file_storage.file_storage_manager import FileStorageManager

from uuid import uuid4
import os

router = APIRouter()

# 这个接口要加鉴权，否则匿名用户可以无限上传
@router.post("/generate-upload-link", response_model=UploadLinkResponse, response_model_exclude_unset=True)
async def generate_upload_link(
    req: UploadLinkRequest = Body(...),
):
    """获取上传链接"""
    file_extension = os.path.splitext(req.filename)[1]
    id = uuid4()
    key = f'uploads/{id}{file_extension}'
  
    file_storage_manager = FileStorageManager()

    file_storage = file_storage_manager.load("s3", CredentialsSchemaBase(
        type="aws",
        name="aws s3",
        data={
            "region": os.getenv("S3_REGION"),
            "use_ssl": os.getenv("S3_SSL"),
            "endpoint": os.getenv("S3_ENDPOINT"),
            "bucket": os.getenv("S3_BUCKET"),
            "secret_key": os.getenv("S3_SECRET_KEY"),
            "access_key": os.getenv("S3_ACCESS_KEY"),
        },
    ))

    url = await file_storage.generate_presigned_url(key)
    return UploadLinkResponse(
        url=url,
    )