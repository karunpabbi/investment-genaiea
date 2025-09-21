from __future__ import annotations

from typing import List

from ..models import AnalysisResult, InvestorPreferences, StartupProfile
from .public_data import get_public_data_aggregator
from .report import get_report_generator
from .scoring import get_scoring_engine
from .vertex_ai import get_vertex_client
from .bigquery import get_bigquery_client


class AnalysisPipeline:
    def __init__(self) -> None:
        self._public_data = get_public_data_aggregator()
        self._reports = get_report_generator()
        self._scoring = get_scoring_engine()
        self._vertex = get_vertex_client()
        self._bigquery = get_bigquery_client()

    def run(self, startup: StartupProfile, preferences: InvestorPreferences) -> AnalysisResult:
        startup.public_signals = self._public_data.gather_signals(startup.name)
        benchmarks = self._bigquery.fetch_sector_benchmarks(startup.sector)

        strengths, risks = self._derive_strengths_and_risks(startup)

        component_scores = self._scoring.score(startup, preferences)
        total_score = self._scoring.total_score(component_scores)

        context_chunks = [doc.extracted_text for doc in startup.documents if doc.extracted_text]
        context_chunks.extend(signal.summary for signal in startup.public_signals)

        summary_note = self._vertex.generate_deal_notes(
            prompt="Generate a concise investment summary with recommendation and grading.",
            context_chunks=context_chunks,
            output_type="summary",
        )
        detailed_note = self._vertex.generate_deal_notes(
            prompt="Generate a detailed investment memo including benchmarks, risks, and diligence flags.",
            context_chunks=context_chunks,
            output_type="detailed",
        )
        founder_note = self._vertex.generate_deal_notes(
            prompt="Summarize founder background, team structure, and capability risks.",
            context_chunks=context_chunks,
            output_type="founder",
        )

        analysis = AnalysisResult(
            startup=startup,
            investor_preferences=preferences,
            strengths=strengths,
            risks=risks,
            benchmarks=benchmarks,
            score_breakdown=component_scores,
            total_score=total_score,
            summary_note=summary_note,
            detailed_note=detailed_note,
            founder_profile_note=founder_note,
        )

        artifacts = self._reports.create_reports(analysis)
        analysis.artifacts = artifacts
        return analysis

    def _derive_strengths_and_risks(self, startup: StartupProfile) -> tuple[List[str], List[str]]:
        metrics = startup.metrics
        strengths: List[str] = []
        risks: List[str] = []
        signals = {
            "market_size_quality": ("Large and well-defined market opportunity", "Market sizing needs validation"),
            "team_strength": ("Seasoned founding team with complementary skills", "Team depth appears thin"),
            "traction_velocity": ("Notable traction momentum", "Limited traction data"),
            "technology_moat": ("Defensible technology or IP position", "Technology moat unclear"),
            "financial_rigour": ("Sound financial discipline", "Financial projections unsubstantiated"),
            "regulatory_readiness": ("Clear regulatory pathway", "Regulatory complexity requires attention"),
        }
        for key, (positive, negative) in signals.items():
            value = metrics.get(key, 0.5)
            try:
                score = float(value)
            except (TypeError, ValueError):
                score = 0.5
            if score >= 0.6:
                strengths.append(positive)
            elif score <= 0.4:
                risks.append(negative)
        return strengths, risks


_analysis_pipeline: AnalysisPipeline | None = None


def get_analysis_pipeline() -> AnalysisPipeline:
    global _analysis_pipeline
    if _analysis_pipeline is None:
        _analysis_pipeline = AnalysisPipeline()
    return _analysis_pipeline
