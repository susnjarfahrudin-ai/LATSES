from dataclasses import dataclass
from typing import Sequence

from .claim import ScientificClaim
from .confidence import ConfidenceScore
from .evidence import ScientificEvidence
from .method import ScientificMethod
from .validation_state import KnowledgeState


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    state: KnowledgeState
    confidence: ConfidenceScore
    reason: str


class KnowledgeValidator:
    """Validates claim support without asserting that nature itself is true."""

    def validate(
        self,
        claim: ScientificClaim,
        evidence: Sequence[ScientificEvidence] | None,
        method: ScientificMethod | None,
        confidence: ConfidenceScore,
        requested_state: KnowledgeState = KnowledgeState.VALIDATED,
    ) -> ValidationResult:
        evidence = tuple(evidence or ())
        if not claim or not claim.claim_id or not claim.domain.strip():
            return ValidationResult(False, KnowledgeState.UNKNOWN, confidence, "Invalid claim identity or domain")
        if not evidence:
            return ValidationResult(False, KnowledgeState.HYPOTHESIS, confidence, "Evidence is required for validation")
        if any(not item.is_verified or not item.provenance_id.strip() for item in evidence):
            return ValidationResult(False, KnowledgeState.HYPOTHESIS, confidence, "Evidence integrity or provenance is insufficient")
        if method is None or not method.procedure.strip() or not method.limitations.strip():
            return ValidationResult(False, KnowledgeState.HYPOTHESIS, confidence, "Methodology is required")

        score = confidence.calculate()
        if requested_state == KnowledgeState.CONFIRMED:
            if score < 0.9 or confidence.evidence_score < 0.9 or confidence.provenance_score < 0.9:
                return ValidationResult(False, KnowledgeState.VALIDATED, confidence, "Evidence/provenance confidence is insufficient for CONFIRMED")
            return ValidationResult(True, KnowledgeState.CONFIRMED, confidence, "Complete evidence chain supports CONFIRMED state")

        if requested_state == KnowledgeState.VALIDATED and score >= 0.75:
            return ValidationResult(True, KnowledgeState.VALIDATED, confidence, "Evidence, method and provenance satisfy validation criteria")

        return ValidationResult(True, KnowledgeState.SUPPORTED, confidence, "Claim has traceable support but does not meet VALIDATED threshold")
