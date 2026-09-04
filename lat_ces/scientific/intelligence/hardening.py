from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class HardeningAssessment:
    status: str
    reason: str
    safe_mode: bool = False

class InputValidationHardening:
    def validate(self, data: object, provenance: tuple[str, ...], timestamp: str) -> HardeningAssessment:
        if data is None:
            return HardeningAssessment("SAFE_MODE_TRIGGERED", "NULL DATA", True)
        if not provenance:
            return HardeningAssessment("REJECTED", "MISSING PROVENANCE")
        if not timestamp.strip():
            return HardeningAssessment("REJECTED", "INVALID TIMESTAMP")
        return HardeningAssessment("VALID", "INPUT ACCEPTED")

class AdversarialDetectionEngine:
    def detect_circular_dependency(self, source: str, target: str, reverse_source: str, reverse_target: str) -> HardeningAssessment:
        if source == reverse_target and target == reverse_source:
            return HardeningAssessment("CIRCULAR_DEPENDENCY_DETECTED", "Mutual support cycle detected")
        return HardeningAssessment("CLEAN", "No direct circular dependency")

class KnowledgeGrounding:
    def require_grounding(self, evidence: tuple[str, ...], source: str, reasoning_trace: tuple[str, ...], confidence: float) -> HardeningAssessment:
        if not evidence or not source.strip() or not reasoning_trace:
            return HardeningAssessment("NO_CLAIM", "Grounding requirements not satisfied")
        if not 0.0 <= confidence <= 1.0:
            return HardeningAssessment("REJECTED", "Invalid confidence")
        return HardeningAssessment("GROUNDED", "Evidence, source and trace present")

class ConfidenceCalibration:
    def calibrate(self, raw_confidence: float, evidence_quality: float) -> float:
        if not 0.0 <= raw_confidence <= 1.0 or not 0.0 <= evidence_quality <= 1.0:
            raise ValueError("Confidence inputs must be within [0, 1]")
        return min(raw_confidence, evidence_quality)

class SafeMode:
    STATES = ("NORMAL", "WARNING", "SAFE_ANALYSIS_MODE", "HUMAN_REVIEW_REQUIRED")
    def require_human_review(self, reason: str) -> HardeningAssessment:
        return HardeningAssessment("HUMAN_REVIEW_REQUIRED", reason, True)
