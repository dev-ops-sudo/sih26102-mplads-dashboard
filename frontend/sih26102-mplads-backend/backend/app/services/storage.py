from __future__ import annotations

from pathlib import Path
from urllib.parse import quote
from uuid import uuid4
from hashlib import sha256

import boto3

from app.config import settings


class UploadService:
    def __init__(self) -> None:
        self.local_root = settings.local_upload_dir.resolve()
        self.local_root.mkdir(parents=True, exist_ok=True)

    def object_key(self, project_id: str, stage: str, filename: str) -> str:
        safe_name = "".join(char for char in Path(filename).name if char.isalnum() or char in {".", "-", "_"})
        return f"projects/{project_id}/{stage}/{uuid4().hex}-{safe_name or 'evidence.bin'}"

    def s3_client(self, public: bool = False):
        endpoint_url = settings.s3_public_endpoint_url if public else settings.s3_endpoint_url
        return boto3.client(
            "s3",
            endpoint_url=endpoint_url or settings.s3_endpoint_url,
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
        )

    def presign(self, project_id: str, stage: str, filename: str, content_type: str) -> dict:
        object_key = self.object_key(project_id, stage, filename)
        if settings.storage_backend == "s3":
            client = self.s3_client(public=True)
            upload_url = client.generate_presigned_url(
                "put_object",
                Params={"Bucket": settings.s3_bucket, "Key": object_key, "ContentType": content_type},
                ExpiresIn=900,
            )
            return {
                "upload_url": upload_url,
                "object_key": object_key,
                "method": "PUT",
                "headers": {"Content-Type": content_type},
            }

        return {
            "upload_url": f"{settings.api_prefix}/uploads/local/{quote(object_key)}",
            "object_key": object_key,
            "method": "PUT",
            "headers": {"Content-Type": content_type},
        }

    def local_path(self, object_key: str) -> Path:
        candidate = (self.local_root / object_key).resolve()
        if self.local_root not in candidate.parents:
            raise ValueError("Invalid object key")
        candidate.parent.mkdir(parents=True, exist_ok=True)
        return candidate

    def object_url(self, object_key: str) -> str:
        return f"{settings.api_prefix}/uploads/download/{quote(object_key)}"

    def presigned_download(self, object_key: str) -> str:
        return self.s3_client(public=True).generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.s3_bucket, "Key": object_key},
            ExpiresIn=300,
        )

    def object_exists(self, object_key: str) -> bool:
        if settings.storage_backend == "s3":
            try:
                self.s3_client().head_object(Bucket=settings.s3_bucket, Key=object_key)
                return True
            except Exception:
                return False
        path = self.local_path(object_key)
        return path.exists() and path.is_file()

    def local_checksum(self, object_key: str) -> str | None:
        if settings.storage_backend != "local":
            return None
        path = self.local_path(object_key)
        if not path.exists() or not path.is_file():
            return None
        digest = sha256()
        with path.open("rb") as evidence_file:
            for chunk in iter(lambda: evidence_file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


upload_service = UploadService()
