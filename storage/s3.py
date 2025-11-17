import os
from typing import Any, Dict


class S3Like:
    def __init__(self, base_dir: str = "artifacts") -> None:
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def upload_bytes(self, key: str, data: bytes, metadata: Dict[str, Any] | None = None) -> str:
        path = os.path.join(self.base_dir, key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        return path

    def download_bytes(self, key: str) -> bytes:
        path = os.path.join(self.base_dir, key)
        with open(path, "rb") as f:
            return f.read()


