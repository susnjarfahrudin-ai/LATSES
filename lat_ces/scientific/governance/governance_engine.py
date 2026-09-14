from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

from .audit import AuditRecord, VerificationRecord
from .authority import Authority
from .rules import GovernanceRule
from lat_ces.scientific.evidence_state import EvidenceState


class ScientificKnowledgeGovernanceEngine:
    """Canonical execution point for the existing verification authority boundary."""

    VERIFY_ACTION = "VERIFY_EVIDENCE"
    GRANT_ACTION = "GRANT_VERIFICATION_AUTHORITY"

    def __init__(self) -> None:
        self.rules: list[GovernanceRule] = []
        self.audit: list[object] = []
        self._authority_grants: dict[str, Authority] = {}
        self._verification_records: dict[str, VerificationRecord] = {}

    def register_rule(self, rule: GovernanceRule) -> None:
        if any(item.rule_id == rule.rule_id and item != rule for item in self.rules):
            raise ValueError(f"Duplicate governance rule: {rule.rule_id}")
        if rule not in self.rules:
            self.rules.append(rule)

    def evaluate_change(self, change: object) -> dict[str, object]:
        if change is None:
            raise ValueError("Governance change proposal cannot be empty")
        return {"change": change, "status": "UNDER_REVIEW"}

    def grant_verification_authority(
        self,
        *,
        grantor: Authority,
        verifier_identity: str,
        scope: str,
        evidence_type: str = "*",
        domain: str = "*",
        method: str = "*",
        purpose: str = "verification",
        valid_from: str = "",
        valid_until: str = "",
    ) -> Authority:
        if not verifier_identity.strip() or not scope.strip():
            raise ValueError("Verification authority requires verifier identity and scope")
        if grantor.action != self.GRANT_ACTION or not grantor.is_valid_now():
            raise PermissionError("Grantor does not hold valid authority to grant verification authority")
        if grantor.identity == verifier_identity:
            raise PermissionError("A verifier cannot grant verification authority to itself")
        grant = Authority(
            identity=verifier_identity,
            level=grantor.level,
            scope=scope,
            action=self.VERIFY_ACTION,
            evidence_type=evidence_type,
            domain=domain,
            method=method,
            purpose=purpose,
            grantor=grantor.identity,
            grant_id=f"AUTH-{uuid4().hex.upper()}",
            valid_from=valid_from,
            valid_until=valid_until,
        )
        self._authority_grants[grant.grant_id] = grant
        self.audit.append(
            AuditRecord(
                action="GRANT_VERIFICATION_AUTHORITY",
                actor=grantor.identity,
                object_id=grant.grant_id,
                reason=purpose,
                result=verifier_identity,
            )
        )
        return grant

    def revoke_authority(self, grant_id: str, *, actor: Authority) -> Authority:
        grant = self._authority_grants.get(grant_id)
        if grant is None:
            raise KeyError(grant_id)
        if actor.identity != grant.grantor and actor.action != self.GRANT_ACTION:
            raise PermissionError("Only the grantor or a valid authority administrator may revoke a grant")
        revoked = replace(grant, revoked=True)
        self._authority_grants[grant_id] = revoked
        self.audit.append(
            AuditRecord(
                action="REVOKE_VERIFICATION_AUTHORITY",
                actor=actor.identity,
                object_id=grant_id,
                reason="authority revoked",
                result="REVOKED",
            )
        )
        return revoked

    def _require_verification_authority(
        self,
        *,
        authority: Authority,
        evidence_type: str,
        domain: str,
        method: str,
    ) -> Authority:
        registered = self._authority_grants.get(authority.grant_id)
        if registered is None:
            raise PermissionError("Verification authority is not a registered grant")
        if registered.identity != authority.identity or registered.action != authority.action:
            raise PermissionError("Verification authority is not a registered grant")
        if not registered.is_valid_now():
            raise PermissionError("Verification authority is expired or revoked")
        if not registered.permits(
            action=self.VERIFY_ACTION,
            evidence_type=evidence_type,
            domain=domain,
            method=method,
        ):
            raise PermissionError("Verification authority scope does not cover this evidence")
        return registered

    def verify_evidence(
        self,
        evidence: object,
        *,
        authority: Authority,
        method: str,
        criteria: str,
        reference: str,
        integrity: str,
        limitations: str,
        domain: str = "",
    ) -> object:
        evidence_id = getattr(evidence, "measurement_id", getattr(evidence, "evidence_id", ""))
        revision = int(getattr(evidence, "revision", 1))
        evidence_type = type(evidence).__name__
        if not evidence_id:
            raise ValueError("Evidence requires an identity")
        if revision < 1:
            raise ValueError("Evidence revision must be >= 1")
        if not all(value.strip() for value in (method, criteria, reference, integrity, limitations)):
            raise ValueError("Verification requires method, criteria, reference, integrity and limitations")
        self._require_verification_authority(
            authority=authority,
            evidence_type=evidence_type,
            domain=domain,
            method=method,
        )
        record = VerificationRecord(
            record_id=f"VER-{uuid4().hex.upper()}",
            evidence_id=evidence_id,
            evidence_revision=revision,
            verifier=authority.identity,
            authority_grant_id=authority.grant_id,
            method=method,
            criteria=criteria,
            reference=reference,
            integrity=integrity,
            limitations=limitations,
            verified_at=datetime.now(timezone.utc).isoformat(),
        )
        self._verification_records[record.record_id] = record
        self.audit.append(record.audit_record())

        if hasattr(evidence, "evidence_state"):
            return replace(
                evidence,
                evidence_state=EvidenceState.VERIFIED,
                verification_record_id=record.record_id,
            )
        if hasattr(evidence, "integrity_status"):
            return replace(
                evidence,
                integrity_status=EvidenceState.VERIFIED.value,
                verification_record_id=record.record_id,
            )
        raise TypeError("Unsupported evidence representation for canonical verification")

    def get_verification_record(self, record_id: str) -> VerificationRecord:
        try:
            return self._verification_records[record_id]
        except KeyError as exc:
            raise KeyError(f"Unknown verification record: {record_id}") from exc

    def is_verified_by_record(self, evidence: object) -> bool:
        record_id = getattr(evidence, "verification_record_id", "")
        if not record_id:
            return False
        record = self._verification_records.get(record_id)
        if record is None:
            return False
        evidence_id = getattr(evidence, "measurement_id", getattr(evidence, "evidence_id", ""))
        revision = int(getattr(evidence, "revision", 1))
        return record.evidence_id == evidence_id and record.evidence_revision == revision
