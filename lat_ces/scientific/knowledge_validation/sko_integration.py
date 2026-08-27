from dataclasses import dataclass, field

from .claim import ScientificClaim
from .confidence import ConfidenceScore
from .conflict import KnowledgeConflict
from .evidence import ScientificEvidence
from .method import ScientificMethod
from .validation_state import KnowledgeState


@dataclass(frozen=True)
class ScientificKnowledgeValidationRecord:
    claim: ScientificClaim
    evidence: tuple[ScientificEvidence, ...]
    method: ScientificMethod | None
    provenance_ids: tuple[str, ...]
    validation_state: KnowledgeState
    confidence: ConfidenceScore
    revision_history: tuple[KnowledgeState, ...] = field(default_factory=tuple)
    conflicts: tuple[KnowledgeConflict, ...] = field(default_factory=tuple)

    def with_state(self, state: KnowledgeState) -> "ScientificKnowledgeValidationRecord":
        return ScientificKnowledgeValidationRecord(
            claim=self.claim,
            evidence=self.evidence,
            method=self.method,
            provenance_ids=self.provenance_ids,
            validation_state=state,
            confidence=self.confidence,
            revision_history=self.revision_history + (state,),
            conflicts=self.conflicts,
        )

    def with_conflict(self, conflict: KnowledgeConflict) -> "ScientificKnowledgeValidationRecord":
        return ScientificKnowledgeValidationRecord(
            claim=self.claim,
            evidence=self.evidence,
            method=self.method,
            provenance_ids=self.provenance_ids,
            validation_state=self.validation_state,
            confidence=self.confidence,
            revision_history=self.revision_history,
            conflicts=self.conflicts + (conflict,),
        )
