from __future__ import annotations
from dataclasses import dataclass
from uuid import uuid4

@dataclass(frozen=True)
class IntelligenceRecommendation:
    recommendation_id: str
    inputs: tuple[str, ...]
    analysis: str
    evidence: tuple[str, ...]
    confidence: float

class ScientificKnowledgeEcosystemIntelligenceEngine:
    def analyze(self, inputs: tuple[str, ...], analysis: str, evidence: tuple[str, ...], confidence: float) -> IntelligenceRecommendation:
        if not inputs or not analysis.strip() or not evidence:
            raise ValueError("Intelligence analysis requires inputs, explanation and evidence")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Intelligence confidence must be within [0, 1]")
        return IntelligenceRecommendation(f"INT-{uuid4().hex.upper()}", tuple(inputs), analysis, tuple(evidence), confidence)
