"""LAT-CES SCI 0062-0145 canonical Scientific Core integration.

This module provides the minimal reference contracts for the dependency chain
from Knowledge Ontology through Adaptive Security Governance. It intentionally
keeps the contracts deterministic, provenance-aware, immutable at the record
boundary, and explicit about human/AI responsibility.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Mapping, Tuple


class KnowledgeState(str, Enum):
    UNKNOWN = "UNKNOWN"
    HYPOTHESIS = "HYPOTHESIS"
    SUPPORTED = "SUPPORTED"
    VALIDATED = "VALIDATED"
    CONFIRMED = "CONFIRMED"


@dataclass(frozen=True)
class ScientificClaim:
    claim_id: str
    statement: str
    domain: str


@dataclass(frozen=True)
class ScientificEvidence:
    evidence_id: str
    evidence_type: str
    source: str
    provenance_id: str
    integrity_status: str


@dataclass(frozen=True)
class ScientificMethod:
    method_id: str
    procedure: str
    parameters: Tuple[Tuple[str, Any], ...] = ()
    limitations: str = ""


@dataclass(frozen=True)
class ConfidenceScore:
    evidence: float
    method: float
    provenance: float
    reference: float

    def value(self) -> float:
        values = (self.evidence, self.method, self.provenance, self.reference)
        if any(not 0.0 <= value <= 1.0 for value in values):
            raise ValueError("Confidence components must be within [0, 1].")
        return sum(values) / 4.0


@dataclass(frozen=True)
class KnowledgeConflict:
    claim_a: str
    claim_b: str
    evidence_a: str
    evidence_b: str
    status: str = "OPEN"


@dataclass(frozen=True)
class ScientificKnowledgeValidationRecord:
    claim: ScientificClaim
    evidence: Tuple[ScientificEvidence, ...]
    method: ScientificMethod
    provenance: Tuple[str, ...]
    reference_knowledge: Tuple[str, ...] = ()
    state: KnowledgeState = KnowledgeState.UNKNOWN
    confidence: ConfidenceScore = field(default_factory=lambda: ConfidenceScore(0, 0, 0, 0))
    conflicts: Tuple[KnowledgeConflict, ...] = ()
    revision: int = 1

    def canonical_hash(self) -> str:
        payload = {
            "claim": self.claim.__dict__,
            "evidence": [item.__dict__ for item in self.evidence],
            "method": {
                "method_id": self.method.method_id,
                "procedure": self.method.procedure,
                "parameters": list(self.method.parameters),
                "limitations": self.method.limitations,
            },
            "provenance": list(self.provenance),
            "reference_knowledge": list(self.reference_knowledge),
            "state": self.state.value,
            "confidence": self.confidence.__dict__,
            "conflicts": [item.__dict__ for item in self.conflicts],
            "revision": self.revision,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return sha256(raw.encode("utf-8")).hexdigest()


class ScientificKnowledgeValidator:
    """Validates evidence chains; it does not manufacture scientific truth."""

    def validate(
        self,
        claim: ScientificClaim,
        evidence: Tuple[ScientificEvidence, ...],
        method: ScientificMethod | None,
        provenance: Tuple[str, ...],
    ) -> bool:
        if not claim.claim_id or not claim.statement.strip() or not claim.domain.strip():
            return False
        if not evidence or any(item.integrity_status != "VERIFIED" for item in evidence):
            return False
        if any(not item.source or not item.provenance_id for item in evidence):
            return False
        if method is None or not method.procedure.strip() or not method.limitations.strip():
            return False
        return bool(provenance)


@dataclass(frozen=True)
class OntologyEntity:
    entity_id: str
    label: str
    domain: str
    definition: str


@dataclass(frozen=True)
class OntologyRelation:
    subject_id: str
    predicate: str
    object_id: str
    provenance_id: str


@dataclass(frozen=True)
class KnowledgeGraph:
    entities: Tuple[OntologyEntity, ...] = ()
    relations: Tuple[OntologyRelation, ...] = ()

    def connected(self, subject_id: str, object_id: str) -> bool:
        return any(
            relation.subject_id == subject_id and relation.object_id == object_id
            for relation in self.relations
        )


@dataclass(frozen=True)
class ReasoningStep:
    premises: Tuple[str, ...]
    rule: str
    conclusion: str
    trace: Tuple[str, ...]


@dataclass(frozen=True)
class SynthesisResult:
    inputs: Tuple[str, ...]
    output: str
    lineage: Tuple[str, ...]
    uncertainty: str


@dataclass(frozen=True)
class KnowledgeRevision:
    previous_revision: int
    revision: int
    reason: str
    lineage: Tuple[str, ...]


@dataclass(frozen=True)
class PreservationRecord:
    object_id: str
    content_hash: str
    archive_reference: str
    retention_policy: str


@dataclass(frozen=True)
class TrustAssessment:
    confidence: ConfidenceScore
    evidence_ids: Tuple[str, ...]
    assessed_at: str


@dataclass(frozen=True)
class AssuranceDecision:
    decision_id: str
    state: str
    rationale: str
    required_controls: Tuple[str, ...]


@dataclass(frozen=True)
class EcosystemSnapshot:
    nodes: Tuple[str, ...]
    relationships: Tuple[str, ...]
    conflicts: Tuple[str, ...]
    health: str


@dataclass(frozen=True)
class IntelligenceAssessment:
    observations: Tuple[str, ...]
    risks: Tuple[str, ...]
    recommendations: Tuple[str, ...]
    human_decision_required: bool = True


@dataclass(frozen=True)
class GovernanceDecision:
    decision_id: str
    actor: str
    policy: str
    authorized: bool
    audit_reference: str


@dataclass(frozen=True)
class SecurityEvent:
    event_id: str
    event_type: str
    severity: str
    action: str
    evidence_reference: str


@dataclass(frozen=True)
class AdaptiveSecurityState:
    risk_level: str
    active_controls: Tuple[str, ...]
    recovery_point: str
    human_oversight_required: bool = True


SCI_0062_0145_CHAIN: Tuple[str, ...] = (
    "0062-0065 Ontology",
    "0066-0069 Reasoning",
    "0070-0073 Synthesis",
    "0074-0077 Evolution",
    "0078-0081 Governance",
    "0082-0085 Preservation",
    "0086-0089 Integrity & Trust",
    "0090-0093 Assurance",
    "0094-0097 Lifecycle",
    "0098-0101 Ecosystem Management",
    "0102-0105 Ecosystem Intelligence",
    "0106-0109 Intelligence Hardening",
    "0110-0113 Intelligence Governance",
    "0114-0117 Governance Hardening",
    "0118-0121 Governance Evolution",
    "0122-0125 Ecosystem Integration",
    "0126-0129 Governance Federation",
    "0130-0133 Federation Security Architecture",
    "0134-0137 Security Hardening",
    "0138-0141 Security Hardening Governance",
    "0142-0145 Adaptive Security Governance",
)

__all__ = [
    "KnowledgeState",
    "ScientificClaim",
    "ScientificEvidence",
    "ScientificMethod",
    "ConfidenceScore",
    "KnowledgeConflict",
    "ScientificKnowledgeValidationRecord",
    "ScientificKnowledgeValidator",
    "OntologyEntity",
    "OntologyRelation",
    "KnowledgeGraph",
    "ReasoningStep",
    "SynthesisResult",
    "KnowledgeRevision",
    "PreservationRecord",
    "TrustAssessment",
    "AssuranceDecision",
    "EcosystemSnapshot",
    "IntelligenceAssessment",
    "GovernanceDecision",
    "SecurityEvent",
    "AdaptiveSecurityState",
    "SCI_0062_0145_CHAIN",
]
