from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import InvestorPreferences, StartupProfile
from ..schemas import AnalysisRequest, AnalysisResponse, AnalysisSummary, ReportArtifact
from ..services.analysis import get_analysis_pipeline
from ..services.ingestion import get_ingestion_service


router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/run", response_model=AnalysisResponse)
async def run_analysis(payload: AnalysisRequest) -> AnalysisResponse:
    ingestion = get_ingestion_service()
    documents = ingestion.get_documents(payload.document_ids)
    if not documents:
        raise HTTPException(status_code=400, detail="No documents available for analysis")

    startup = StartupProfile(
        name=payload.preferences.startup_name,
        sector=payload.preferences.sector,
        headquarters=payload.preferences.headquarters,
        description=payload.preferences.description or "",
        documents=documents,
    )

    preferences = InvestorPreferences(
        focus_weights=payload.preferences.focus_weights,
        notes=payload.preferences.notes,
    )

    pipeline = get_analysis_pipeline()
    analysis = pipeline.run(startup, preferences)

    artifacts = [
        ReportArtifact(label=label, url=str(path))
        for label, path in analysis.artifacts.items()
    ]

    return AnalysisResponse(
        startup_name=analysis.startup.name,
        total_score=analysis.total_score,
        score_breakdown=analysis.score_breakdown,
        strengths=analysis.strengths,
        risks=analysis.risks,
        benchmarks=analysis.benchmarks,
        summary_note=analysis.summary_note,
        detailed_note=analysis.detailed_note,
        founder_profile_note=analysis.founder_profile_note,
        artifacts=artifacts,
    )
