from __future__ import annotations

from typing import Dict, Iterable

from ..models import InvestorPreferences, StartupProfile


DEFAULT_PARAMETERS = {
    "market": "Market Size & Velocity",
    "team": "Founder & Team Strength",
    "traction": "Traction & Growth",
    "technology": "Technology & Defensibility",
    "financials": "Financial Quality",
    "regulatory": "Regulatory Fit",
}


class ScoringEngine:
    def __init__(self, parameters: Dict[str, str] | None = None) -> None:
        self.parameters = parameters or DEFAULT_PARAMETERS

    def score(self, startup: StartupProfile, preferences: InvestorPreferences) -> Dict[str, float]:
        normalized = preferences.normalized()
        base_scores = self._baseline_scores(startup)
        results: Dict[str, float] = {}
        for key, label in self.parameters.items():
            base = base_scores.get(key, 0.5)
            weight = normalized.get(key, 0)
            results[key] = float(base * weight)
        return results

    def total_score(self, component_scores: Dict[str, float]) -> float:
        return float(sum(component_scores.values()))

    def _baseline_scores(self, startup: StartupProfile) -> Dict[str, float]:
        metrics = startup.metrics
        def norm_metric(name: str, fallback: float) -> float:
            value = metrics.get(name, fallback)
            try:
                return float(value)
            except (TypeError, ValueError):
                return fallback

        return {
            "market": min(norm_metric("market_size_quality", 0.6), 1.0),
            "team": min(norm_metric("team_strength", 0.6), 1.0),
            "traction": min(norm_metric("traction_velocity", 0.5), 1.0),
            "technology": min(norm_metric("technology_moat", 0.5), 1.0),
            "financials": min(norm_metric("financial_rigour", 0.4), 1.0),
            "regulatory": min(norm_metric("regulatory_readiness", 0.5), 1.0),
        }


_scoring_engine: ScoringEngine | None = None


def get_scoring_engine() -> ScoringEngine:
    global _scoring_engine
    if _scoring_engine is None:
        _scoring_engine = ScoringEngine()
    return _scoring_engine
