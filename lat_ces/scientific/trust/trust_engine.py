from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ScientificKnowledgeTrustObject:
    knowledge_id: str
    integrity_score: float
    evidence_score: float
    confidence: float
    risk: str

@dataclass(frozen=True)
class TrustAssessment:
    trust_score: float
    confidence_class: str
    risk: str
    history_id: str = ""

class IntegrityManager:
    def evaluate(self, integrity_ok: bool) -> float:
        return 1.0 if integrity_ok else 0.0

class EvidenceScorer:
    def score(self, evidence_score: float) -> float:
        if not 0.0 <= evidence_score <= 1.0:
            raise ValueError("Evidence score must be within [0, 1]")
        return evidence_score

class ConfidenceModel:
    def classify(self, score: float) -> str:
        if not 0.0 <= score <= 1.0:
            raise ValueError("Confidence must be within [0, 1]")
        if score >= 0.9: return "CONFIRMED"
        if score >= 0.75: return "VALIDATED"
        if score >= 0.5: return "SUPPORTED"
        return "HYPOTHESIS"

class RiskAssessment:
    def classify(self, score: float) -> str:
        if not 0.0 <= score <= 1.0:
            raise ValueError("Risk score must be within [0, 1]")
        return "LOW" if score < 0.25 else "MEDIUM" if score < 0.6 else "HIGH"

class TrustModel:
    def calculate(self, evidence: float, validation: float, provenance: float, governance: float, reproducibility: float) -> float:
        values = (evidence, validation, provenance, governance, reproducibility)
        if any(not 0.0 <= value <= 1.0 for value in values):
            raise ValueError("Trust inputs must be within [0, 1]")
        return round(sum(values) / len(values), 12)

class ScientificKnowledgeTrustEngine:
    def assess(self, knowledge_id: str, *, evidence: float, validation: float, provenance: float, governance: float, reproducibility: float) -> TrustAssessment:
        score = TrustModel().calculate(evidence, validation, provenance, governance, reproducibility)
        return TrustAssessment(score, ConfidenceModel().classify(score), RiskAssessment().classify(1.0 - score))
