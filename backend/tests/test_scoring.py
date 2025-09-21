from __future__ import annotations

from app.models import InvestorPreferences, StartupProfile
from app.services.scoring import ScoringEngine


def test_scoring_normalization():
    startup = StartupProfile(
        name="TestCo",
        sector="AI",
        headquarters="NYC",
        description="",
        metrics={
            "market_size_quality": 0.8,
            "team_strength": 0.6,
            "traction_velocity": 0.7,
            "technology_moat": 0.5,
            "financial_rigour": 0.4,
            "regulatory_readiness": 0.3,
        },
        documents=[],
    )
    preferences = InvestorPreferences(
        focus_weights={"market": 40, "team": 30, "traction": 20, "technology": 10},
    )
    engine = ScoringEngine()
    component_scores = engine.score(startup, preferences)
    assert component_scores["market"] > component_scores["technology"]
    total = engine.total_score(component_scores)
    assert 0 <= total <= 1
