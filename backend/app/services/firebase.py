from __future__ import annotations

from pathlib import Path
from typing import Optional

import firebase_admin
from firebase_admin import credentials, storage

from ..config import get_settings


class FirebaseStorage:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._bucket: Optional[storage.bucket.Bucket] = None
        self._init()

    def _init(self) -> None:
        if not self._settings.enable_google_services:
            return
        if self._settings.firebase_storage_bucket is None:
            return
        if not firebase_admin._apps:
            try:
                firebase_admin.initialize_app()
            except ValueError:
                # Allow running without credentials locally
                return
        try:
            self._bucket = storage.bucket(self._settings.firebase_storage_bucket)
        except Exception:
            self._bucket = None

    @property
    def available(self) -> bool:
        return self._bucket is not None

    def upload_file(self, path: Path, destination: str) -> None:
        if not self.available:
            return
        blob = self._bucket.blob(destination)
        blob.upload_from_filename(path)

    def generate_signed_url(self, destination: str, ttl_seconds: int = 86400) -> Optional[str]:
        if not self.available:
            return None
        blob = self._bucket.blob(destination)
        try:
            return blob.generate_signed_url(ttl_seconds)
        except Exception:
            return None
