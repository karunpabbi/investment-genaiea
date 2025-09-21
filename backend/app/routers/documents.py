from __future__ import annotations

from typing import List

from fastapi import APIRouter, File, UploadFile

from ..schemas import UploadResponse
from ..services.ingestion import get_ingestion_service


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)) -> UploadResponse:
    ingestion = get_ingestion_service()
    records = ingestion.save_uploads(files)
    return UploadResponse(document_ids=[record.id for record in records])
