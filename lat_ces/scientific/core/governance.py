from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from typing import Any, Mapping
from uuid import uuid4


class LifecycleState(str, Enum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RETIRED = "RETIRED"


_ALLOWED_TRANSITIONS = {
    LifecycleState.DRAFT: {LifecycleState.VALIDATED, LifecycleState.REJECTED},
    LifecycleState.VALIDATED: {LifecycleState.APPROVED, LifecycleState.REJECTED},
    LifecycleState.APPROVED: {LifecycleState.RETIRED},
    LifecycleState.REJECTED: {LifecycleState.DRAFT},
    LifecycleState.RETIRED: set(),
}


@dataclass(frozen=True)
class ScientificArtifact:
    """Canonical immutable record shared by evolution, governance and trust."""

    artifact_id: str
    sci_id: str
    kind: str
    version: int
    state: LifecycleState
    content: Mapping[str, Any]
    provenance: tuple[str, ...]
    parents: tuple[str, ...] = ()
    uncertainty: float | None = None
    content_hash: str = ""

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "sci_id": self.sci_id,
            "kind": self.kind,
            "version": self.version,
            "state": self.state.value,
            "content": self.content,
            "provenance": self.provenance,
            "parents": self.parents,
            "uncertainty": self.uncertainty,
        }

    def with_hash(self) -> "ScientificArtifact":
        raw = json.dumps(self.canonical_payload(), sort_keys=True, separators=(",", ":"), default=str)
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return replace(self, content_hash=digest)


class ArtifactRegistry:
    def __init__(self) -> None:
        self._items: dict[str, ScientificArtifact] = {}

    def register(self, artifact: ScientificArtifact) -> ScientificArtifact:
        checked = artifact.with_hash()
        current = self._items.get(checked.artifact_id)
        if current is not None and current.content_hash != checked.content_hash:
            raise ValueError(f"Artifact identity collision: {checked.artifact_id}")
        self._items[checked.artifact_id] = checked
        return checked

    def get(self, artifact_id: str) -> ScientificArtifact | None:
        return self._items.get(artifact_id)

    def all(self) -> tuple[ScientificArtifact, ...]:
        return tuple(self._items.values())


@dataclass(frozen=True)
class GovernanceDecision:
    decision_id: str
    artifact_id: str
    authority: str
    decision: str
    rationale: str
    evidence: tuple[str, ...]
    decided_at: str


class GovernanceEngine:
    def __init__(self) -> None:
        self.decisions: list[GovernanceDecision] = []

    def decide(self, *, artifact_id: str, authority: str, decision: str, rationale: str, evidence: tuple[str, ...]) -> GovernanceDecision:
        if not authority.strip() or not decision.strip() or not rationale.strip():
            raise ValueError("Governance decisions require authority, decision and rationale")
        if not evidence:
            raise ValueError("Governance decisions require evidence")
        item = GovernanceDecision(
            decision_id=f"GOV-{uuid4().hex.upper()}",
            artifact_id=artifact_id,
            authority=authority,
            decision=decision,
            rationale=rationale,
            evidence=tuple(evidence),
            decided_at=datetime.now(timezone.utc).isoformat(),
        )
        self.decisions.append(item)
        return item


class EvolutionEngine:
    def revise(self, artifact: ScientificArtifact, *, content: Mapping[str, Any], provenance: tuple[str, ...]) -> ScientificArtifact:
        if not provenance:
            raise ValueError("Evolution requires provenance")
        return ScientificArtifact(
            artifact_id=artifact.artifact_id,
            sci_id=artifact.sci_id,
            kind=artifact.kind,
            version=artifact.version + 1,
            state=LifecycleState.DRAFT,
            content=dict(content),
            provenance=tuple(provenance),
            parents=(artifact.artifact_id,),
            uncertainty=artifact.uncertainty,
        ).with_hash()


class LifecycleEngine:
    def transition(self, artifact: ScientificArtifact, target: LifecycleState) -> ScientificArtifact:
        if target not in _ALLOWED_TRANSITIONS[artifact.state]:
            raise ValueError(f"Illegal lifecycle transition: {artifact.state.value} -> {target.value}")
        return replace(artifact, state=target).with_hash()


class IntegrityTrustEngine:
    def verify(self, artifact: ScientificArtifact) -> bool:
        return bool(artifact.content_hash) and artifact.content_hash == artifact.with_hash().content_hash

    def require_valid(self, artifact: ScientificArtifact) -> ScientificArtifact:
        if not self.verify(artifact):
            raise ValueError(f"Integrity verification failed: {artifact.artifact_id}")
        return artifact


@dataclass(frozen=True)
class AssuranceResult:
    artifact_id: str
    level: str
    reasons: tuple[str, ...]


class AssuranceEngine:
    def assess(self, artifact: ScientificArtifact) -> AssuranceResult:
        reasons: list[str] = []
        if not artifact.provenance:
            reasons.append("missing provenance")
        if not artifact.content_hash:
            reasons.append("missing integrity hash")
        if artifact.uncertainty is not None and artifact.uncertainty < 0:
            reasons.append("negative uncertainty")
        if artifact.state not in {LifecycleState.VALIDATED, LifecycleState.APPROVED}:
            reasons.append("artifact not validated/approved")
        level = "HIGH" if not reasons else "LOW"
        return AssuranceResult(artifact.artifact_id, level, tuple(reasons))


@dataclass(frozen=True)
class PreservationSnapshot:
    artifact_id: str
    snapshot_hash: str
    retention_class: str
    created_at: str


class PreservationEngine:
    def snapshot(self, artifact: ScientificArtifact, *, retention_class: str = "SCIENTIFIC") -> PreservationSnapshot:
        if not retention_class.strip():
            raise ValueError("Preservation requires a retention class")
        return PreservationSnapshot(
            artifact_id=artifact.artifact_id,
            snapshot_hash=artifact.with_hash().content_hash,
            retention_class=retention_class,
            created_at=datetime.now(timezone.utc).isoformat(),
        )


@dataclass(frozen=True)
class EcosystemNode:
    node_id: str
    domain: str
    version: str
    capabilities: tuple[str, ...]


class EcosystemEngine:
    def __init__(self) -> None:
        self.nodes: dict[str, EcosystemNode] = {}
        self.links: set[tuple[str, str]] = set()

    def register(self, node: EcosystemNode) -> EcosystemNode:
        if not node.domain.strip() or not node.version.strip() or not node.capabilities:
            raise ValueError("Ecosystem node requires domain, version and capabilities")
        self.nodes[node.node_id] = node
        return node

    def link(self, source: str, target: str) -> None:
        if source not in self.nodes or target not in self.nodes:
            raise ValueError("Ecosystem link requires registered nodes")
        self.links.add((source, target))


@dataclass(frozen=True)
class IntelligenceRecommendation:
    recommendation_id: str
    rule_id: str
    inputs: tuple[str, ...]
    recommendation: str
    evidence: tuple[str, ...]


class IntelligenceEngine:
    def recommend(self, *, rule_id: str, inputs: tuple[str, ...], recommendation: str, evidence: tuple[str, ...]) -> IntelligenceRecommendation:
        if not rule_id.strip() or not recommendation.strip() or not inputs or not evidence:
            raise ValueError("Intelligence recommendations require rule, inputs, output and evidence")
        return IntelligenceRecommendation(
            recommendation_id=f"REC-{uuid4().hex.upper()}",
            rule_id=rule_id,
            inputs=tuple(inputs),
            recommendation=recommendation,
            evidence=tuple(evidence),
        )


@dataclass(frozen=True)
class FederationEnvelope:
    envelope_id: str
    artifact_id: str
    issuer: str
    audience: str
    payload_hash: str


class FederationEngine:
    def package(self, artifact: ScientificArtifact, *, issuer: str, audience: str) -> FederationEnvelope:
        if not issuer.strip() or not audience.strip():
            raise ValueError("Federation requires issuer and audience")
        return FederationEnvelope(
            envelope_id=f"FED-{uuid4().hex.upper()}",
            artifact_id=artifact.artifact_id,
            issuer=issuer,
            audience=audience,
            payload_hash=artifact.with_hash().content_hash,
        )

    def accept(self, envelope: FederationEnvelope, artifact: ScientificArtifact) -> bool:
        return envelope.artifact_id == artifact.artifact_id and envelope.payload_hash == artifact.with_hash().content_hash


@dataclass(frozen=True)
class SecurityDecision:
    policy_id: str
    subject: str
    action: str
    allowed: bool
    risk: float
    reason: str


class SecurityGovernanceEngine:
    def evaluate(self, *, policy_id: str, subject: str, action: str, risk: float, allowed_actions: frozenset[str]) -> SecurityDecision:
        if not policy_id.strip() or not subject.strip() or not action.strip():
            raise ValueError("Security evaluation requires policy, subject and action")
        if not 0.0 <= risk <= 1.0:
            raise ValueError("Security risk must be between 0 and 1")
        allowed = action in allowed_actions and risk < 0.8
        reason = "policy-and-risk-accepted" if allowed else "policy-or-risk-rejected"
        return SecurityDecision(policy_id, subject, action, allowed, risk, reason)


class AdaptiveSecurityGovernance:
    def adjust_risk(self, *, baseline: float, observed: float, threshold: float = 0.8) -> float:
        if not 0.0 <= baseline <= 1.0 or not 0.0 <= observed <= 1.0 or not 0.0 < threshold <= 1.0:
            raise ValueError("Security risk values must be between 0 and 1")
        return min(1.0, max(baseline, observed) / threshold)


class SecurityMaturity:
    LEVEL_1 = "documented-and-tested"
    LEVEL_2 = "enforced-and-audited"
