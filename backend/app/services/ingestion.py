from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
from uuid import uuid4

from fastapi import UploadFile

from ..config import get_settings
from ..models import DocumentRecord
from .firebase import FirebaseStorage
from .vision import VisionExtractor
from ..utils.file_parsers import extract_text_from_file


class IngestionService:
    """Handles document ingestion and storage pipeline."""

    def __init__(self, storage_dir: Path | None = None) -> None:
        self._settings = get_settings()
        self.storage_dir = storage_dir or Path("storage")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._documents: Dict[str, DocumentRecord] = {}
        self._firebase = FirebaseStorage()
        self._vision = VisionExtractor()

    def save_uploads(self, files: Iterable[UploadFile]) -> List[DocumentRecord]:
        saved_docs: List[DocumentRecord] = []
        for file in files:
            raw_bytes = file.file.read()
            file.file.close()
            extension = Path(file.filename or "upload").suffix
            mime_type, _ = mimetypes.guess_type(file.filename or "upload")
            mime_type = mime_type or file.content_type or "application/octet-stream"

            document_id = str(uuid4())
            local_path = self.storage_dir / f"{document_id}{extension}"
            with local_path.open("wb") as f:
                f.write(raw_bytes)

            if mime_type.startswith("image/"):
                text_content = self._vision.extract_text(raw_bytes)
            else:
                text_content = extract_text_from_file(local_path, raw_bytes)

            record = DocumentRecord(
                id=document_id,
                filename=file.filename or local_path.name,
                content_type=mime_type,
                extracted_text=text_content,
                metadata={"local_path": str(local_path)}
            )
            self._documents[document_id] = record

            # Mirror to Firebase Storage if configured
            if self._firebase.available:
                self._firebase.upload_file(local_path, destination=f"documents/{local_path.name}")

            saved_docs.append(record)
        return saved_docs

    def get_documents(self, document_ids: Iterable[str]) -> List[DocumentRecord]:
        docs: List[DocumentRecord] = []
        for doc_id in document_ids:
            if doc_id not in self._documents:
                continue
            docs.append(self._documents[doc_id])
        return docs

    def clear(self) -> None:
        self._documents.clear()


_ingestion_service: IngestionService | None = None


def get_ingestion_service() -> IngestionService:
    global _ingestion_service
    if _ingestion_service is None:
        _ingestion_service = IngestionService()
    return _ingestion_service
