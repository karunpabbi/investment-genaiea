from __future__ import annotations

from typing import Optional

from google.cloud import vision

from ..config import get_settings


class VisionExtractor:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._client: Optional[vision.ImageAnnotatorClient] = None
        if self._settings.enable_google_services:
            try:
                self._client = vision.ImageAnnotatorClient()
            except Exception:
                self._client = None

    def extract_text(self, raw_bytes: bytes) -> str:
        if self._client is None:
            return ""
        image = vision.Image(content=raw_bytes)
        try:
            response = self._client.document_text_detection(image=image)
        except Exception:
            return ""
        if not response.full_text_annotation:
            return ""
        return response.full_text_annotation.text or ""
