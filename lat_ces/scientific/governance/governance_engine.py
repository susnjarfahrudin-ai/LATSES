from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

from .audit import AuditRecord, VerificationRecord
from .authority import Authority, CanonicalAuthorityRegistry
from .rules import GovernanceRule
from lat_ces.scientific.evidence_state import EvidenceState


class ScientificKnowledgeGovernanceEngine:
    """Canonical execution point for the existing verification authority boundary."""

    VERIFY_ACTION = "VERIFY_EVIDENCE"
    GRANT_ACTION = "GRANT_VERIFICATION_AUTHORITY"

    def __init__(self) -> None:
        self.rules: list[GovernanceRule] = []
        self.audit: list[object] = []
        self.authority_registry = CanonicalAuthorityRegistry()
        self._authority_grants: dict[str, Authority] = {}
        self._verification_records: dict[str, VerificationRecord] = {}

    @property
    def canonical_root_authority(self) -> Authority:
        """Return the root authority from this engine's canonical registry context."""
        return self.authority_registry.root

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
        if not self.authority_registry.is_registered(grantor):
            raise PermissionError("Grantor is not a canonical registered authority")
        self.authority_registry.validate_chain(grantor.grant_id)
        if grantor.identity == verifier_identity:
            raise PermissionError("A verifier cannot grant verification authority to itself")
        if not grantor.permits(
            action=self.GRANT_ACTION,
            evidence_type=evidence_type,
            domain=domain,
            method=method,
            purpose=purpose,
        ):
            raise PermissionError("Grantor authority scope does not cover this verification grant")
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
            parent_grant_id=grantor.grant_id,
            valid_from=valid_from,
            valid_until=valid_until,
        )
        self.authority_registry.register(grant)
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
        self.authority_registry.validate_chain(grant_id)
        if actor.identity != grant.grantor and actor.action != self.GRANT_ACTION:
            raise PermissionError("Only the grantor or a valid authority administrator may revoke a grant")
        self.authority_registry.revoke(grant_id)
        self.audit.append(
            AuditRecord(
                action="REVOKE_VERIFICATION_AUTHORITY",
                actor=actor.identity,
                object_id=grant_id,
                reason="authority revoked",
                result="REVOKED",
            )
        )
        return grant

    def _require_verification_authority(
        self,
        *,
        authority: Authority,
        evidence_type: str,
        domain: str,
        method: str,
        purpose: str = "verification",
    ) -> Authority:
        registered = self._authority_grants.get(authority.grant_id)
        if registered is None or registered is not authority:
            raise PermissionError("Verification authority is not a registered grant")
        if self.authority_registry.is_revoked(registered.grant_id) or not registered.is_valid_now():
            raise PermissionError("Verification authority is expired or revoked")
        self.authority_registry.validate_chain(registered.grant_id)
        if not registered.permits(
            action=self.VERIFY_ACTION,
            evidence_type=evidence_type,
            domain=domain,
            method=method,
            purpose=purpose,
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
        purpose: str = "verification",
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
            purpose=purpose,
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
            evidence_type=evidence_type,
            domain=domain,
            purpose=purpose,
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

    def resolve_verification_record(
        self,
        record_id: str,
        *,
        evidence_id: str,
        evidence_revision: int,
        evidence_type: str = "",
        domain: str = "",
        purpose: str = "verification",
    ) -> VerificationRecord | None:
        """Resolve one canonical verification record for downstream admission.

        Resolution is fail-closed. The record must be registered in this
        governance context, bind to the exact evidence identity/revision,
        and remain backed by a valid canonical authority chain.
        """
        if not record_id.strip() or not evidence_id.strip() or evidence_revision < 1:
            return None
        record = self._verification_records.get(record_id)
        if record is None:
            return None
        if record.evidence_id != evidence_id or record.evidence_revision != evidence_revision:
            return None
        try:
            self.authority_registry.validate_chain(record.authority_grant_id)
        except PermissionError:
            return None
        authority = self._authority_grants.get(record.authority_grant_id)
        if authority is None or record.verifier != authority.identity:
            return None
        if not authority.is_valid_now() or self.authority_registry.is_revoked(authority.grant_id):
            return None
        if evidence_type and record.evidence_type and record.evidence_type != evidence_type:
            return None
        if domain and record.domain and record.domain != domain:
            return None
        if record.purpose != purpose:
            return None
        if not authority.permits(
            action=self.VERIFY_ACTION,
            evidence_type=record.evidence_type or evidence_type,
            domain=record.domain or domain,
            method=record.method,
            purpose=record.purpose,
        ):
            return None
        return record

    def is_verified_by_record(self, evidence: object) -> bool:
        record_id = getattr(evidence, "verification_record_id", "")
        evidence_id = getattr(evidence, "measurement_id", getattr(evidence, "evidence_id", ""))
        revision = int(getattr(evidence, "revision", 1))
        evidence_type = type(evidence).__name__
        return (
            self.resolve_verification_record(
                record_id,
                evidence_id=evidence_id,
                evidence_revision=revision,
                evidence_type=evidence_type,
            )
            is not None
        )
