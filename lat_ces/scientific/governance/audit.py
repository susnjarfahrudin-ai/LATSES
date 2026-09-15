from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class AuditRecord:
    action: str
    actor: str
    object_id: str
    reason: str
    result: str = "RECORDED"
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            object.__setattr__(self, "timestamp", datetime.now(timezone.utc).isoformat())
        if not all(value.strip() for value in (self.action, self.actor, self.object_id, self.reason, self.result)):
            raise ValueError("AuditRecord requires action, actor, object, reason and result")


@dataclass(frozen=True)
class VerificationRecord:
    """Canonical proof that an authorized verifier verified one exact revision."""

    record_id: str
    evidence_id: str
    evidence_revision: int
    verifier: str
    authority_grant_id: str
    method: str
    criteria: str
    reference: str
    integrity: str
    limitations: str
    verified_at: str = ""
    evidence_type: str = ""
    domain: str = ""
    purpose: str = ""

    def __post_init__(self) -> None:
        values = (
            self.record_id,
            self.evidence_id,
            self.verifier,
            self.authority_grant_id,
            self.method,
            self.criteria,
            self.reference,
            self.integrity,
            self.limitations,
        )
        if not all(value.strip() for value in values):
            raise ValueError("VerificationRecord requires complete authority, method and evidence lineage")
        if self.evidence_revision < 1:
            raise ValueError("VerificationRecord evidence_revision must be >= 1")
        if not self.verified_at:
            object.__setattr__(self, "verified_at", datetime.now(timezone.utc).isoformat())

    def audit_record(self) -> AuditRecord:
        return AuditRecord(
            action="VERIFY_EVIDENCE",
            actor=self.verifier,
            object_id=self.evidence_id,
            reason=self.criteria,
            result=self.record_id,
            timestamp=self.verified_at,
        )
