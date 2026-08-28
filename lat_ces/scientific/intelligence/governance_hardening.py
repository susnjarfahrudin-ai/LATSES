from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class GovernanceHardeningResult:
    status: str
    reason: str

class GovernanceIntegrityGuard:
    def verify(self, event: object, expected_hash: str | None = None) -> bool:
        if event is None:
            return False
        if expected_hash is None:
            return True
        return bool(expected_hash)

class AuthorityProtection:
    def protect(self, requested_level: int, max_level: int) -> GovernanceHardeningResult:
        if requested_level > max_level:
            return GovernanceHardeningResult("DENIED", "Authority escalation blocked")
        return GovernanceHardeningResult("ALLOWED", "Authority within boundary")

class AuditIntegrityGuard:
    def protect(self, deletion_requested: bool) -> GovernanceHardeningResult:
        return GovernanceHardeningResult("INTEGRITY_FAILURE_DETECTED", "Audit deletion denied") if deletion_requested else GovernanceHardeningResult("PROTECTED", "Audit append-only")

class GovernanceHardeningEngine:
    def protect(self, event: object, *, requested_level: int = 0, max_level: int = 3, audit_delete: bool = False) -> GovernanceHardeningResult:
        if not self._integrity.verify(event):
            return GovernanceHardeningResult("SAFE_MODE", "Governance integrity failed")
        authority = self._authority.protect(requested_level, max_level)
        if authority.status == "DENIED":
            return authority
        return self._audit.protect(audit_delete)
    def __init__(self) -> None:
        self._integrity = GovernanceIntegrityGuard()
        self._authority = AuthorityProtection()
        self._audit = AuditIntegrityGuard()
