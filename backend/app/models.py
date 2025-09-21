from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class DocumentRecord:
    id: str
    filename: str
    content_type: str
    extracted_text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    uploaded_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class InvestorPreferences:
    focus_weights: Dict[str, float]
    notes: Optional[str] = None

    def normalized(self) -> Dict[str, float]:
        total = sum(self.focus_weights.values())
        if total <= 0:
            return {k: 0 for k in self.focus_weights}
        return {k: v / total for k, v in self.focus_weights.items()}


@dataclass
class PublicSignal:
    source: str
    title: str
    summary: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StartupProfile:
    name: str
    sector: Optional[str]
    headquarters: Optional[str]
    description: str
    founders: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    documents: List[DocumentRecord] = field(default_factory=list)
    public_signals: List[PublicSignal] = field(default_factory=list)


@dataclass
class AnalysisResult:
    startup: StartupProfile
    investor_preferences: InvestorPreferences
    strengths: List[str]
    risks: List[str]
    benchmarks: Dict[str, Any]
    score_breakdown: Dict[str, float]
    total_score: float
    summary_note: str
    detailed_note: str
    founder_profile_note: str
    artifacts: Dict[str, Path] = field(default_factory=dict)
