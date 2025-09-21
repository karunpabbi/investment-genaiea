from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    document_ids: List[str]


class InvestorPreferencesIn(BaseModel):
    startup_name: str = Field(..., examples=["Acme Robotics"])
    sector: Optional[str] = Field(default=None)
    headquarters: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    focus_weights: Dict[str, float] = Field(
        ..., examples=[{"market": 40, "team": 30, "traction": 30}]
    )
    notes: Optional[str] = None


class AnalysisRequest(BaseModel):
    document_ids: List[str]
    preferences: InvestorPreferencesIn


class AnalysisSummary(BaseModel):
    startup_name: str
    total_score: float
    score_breakdown: Dict[str, float]
    strengths: List[str]
    risks: List[str]
    benchmarks: Dict[str, float]
    summary_note: str


class ReportArtifact(BaseModel):
    label: str
    url: str


class AnalysisResponse(AnalysisSummary):
    detailed_note: str
    founder_profile_note: str
    artifacts: List[ReportArtifact]
