import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError


class S3MediaStore:
    """
    真实 S3 媒体存储封装，默认写入 S3，如未提供 Bucket 或显式开启回退则落盘本地。
    支持统一的 key 生成策略与元数据扩展，方便 Audit/回放。
    """

    def __init__(
        self,
        bucket: Optional[str] = None,
        region: Optional[str] = None,
        prefix: Optional[str] = None,
        fallback_dir: str = "artifacts",
        public_url_base: Optional[str] = None,
        force_local: bool = False,
    ) -> None:
        self.bucket = bucket or os.getenv("S3_BUCKET")
        self.region = region or os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
        self.prefix = (prefix or os.getenv("S3_PREFIX") or "media").strip("/")
        self.fallback_dir = Path(fallback_dir or os.getenv("S3_FALLBACK_DIR", "artifacts"))
        self.public_url_base = public_url_base or os.getenv("S3_PUBLIC_URL_BASE")
        self.force_local = force_local or not self.bucket
        self._s3 = None
        if not self.force_local:
            session = boto3.session.Session(region_name=self.region)
            self._s3 = session.client("s3")
        else:
            self.fallback_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def build_key(task_id: str, filename: str, media_type: str = "generic") -> str:
        safe_name = "".join(ch if ch.isalnum() or ch in ("-", "_", ".") else "_" for ch in filename)
        today = datetime.utcnow().strftime("%Y/%m/%d")
        return f"{media_type}/{today}/{task_id}/{safe_name}"

    def upload_media(
        self,
        task_id: str,
        filename: str,
        data: bytes,
        media_type: str = "generic",
        metadata: Optional[Dict[str, Any]] = None,
        content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        key = f"{self.prefix}/{self.build_key(task_id, filename, media_type)}"
        metadata = metadata or {}
        normalized_meta = {str(k): str(v) for k, v in metadata.items()}
        if self.force_local:
            path = self._write_local(key, data)
            return {
                "bucket": "local-fs",
                "key": key,
                "path": str(path),
                "strategy": "local",
                "metadata": normalized_meta,
            }
        try:
            extra: Dict[str, Any] = {"Metadata": normalized_meta}
            if content_type:
                extra["ContentType"] = content_type
            self._s3.put_object(Bucket=self.bucket, Key=key, Body=data, **extra)
            return {
                "bucket": self.bucket,
                "key": key,
                "url": self._build_url(key),
                "strategy": "s3",
                "metadata": normalized_meta,
            }
        except (BotoCoreError, ClientError) as exc:  # pragma: no cover - 网络异常难测
            raise RuntimeError(f"S3 upload failed: {exc}") from exc

    def download_media(self, key: str) -> bytes:
        full_key = key if not key.startswith("/") else key.lstrip("/")
        if self.force_local:
            path = self.fallback_dir / full_key
            with open(path, "rb") as f:
                return f.read()
        try:
            res = self._s3.get_object(Bucket=self.bucket, Key=full_key)
            return res["Body"].read()
        except (BotoCoreError, ClientError) as exc:  # pragma: no cover
            raise RuntimeError(f"S3 download failed: {exc}") from exc

    def _write_local(self, key: str, data: bytes) -> Path:
        path = self.fallback_dir / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def _build_url(self, key: str) -> str:
        if self.public_url_base:
            return f"{self.public_url_base.rstrip('/')}/{key}"
        region = self.region or "us-east-1"
        return f"https://{self.bucket}.s3.{region}.amazonaws.com/{key}"

