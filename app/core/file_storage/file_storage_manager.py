from .file_storage import FileStorage
from .s3_storage import S3Storage
from models.credentials import CredentialsSchemaBase

storage_cls_map = {
    "s3": S3Storage,
    # "oss": OSSStorage,
}

class FileStorageManager:
    def load(self, provider: str, credentials: CredentialsSchemaBase) -> FileStorage:
        cls = storage_cls_map[provider]
        return cls(credentials)