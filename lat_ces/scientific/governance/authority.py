from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Authority:
    """Immutable, action-specific authority grant descriptor.

    The descriptor itself is not authority; the canonical governance engine must
    register the grant before it can authorize a protected transition.
    """

    identity: str
    level: int
    scope: str
    action: str = ""
    evidence_type: str = ""
    domain: str = ""
    method: str = ""
    purpose: str = ""
    grantor: str = ""
    grant_id: str = ""
    valid_from: str = ""
    valid_until: str = ""
    revoked: bool = False

    def __post_init__(self) -> None:
        if not self.identity.strip() or not self.scope.strip() or self.level not in {0, 1, 2, 3}:
            raise ValueError("Authority requires identity, scope and level 0-3")
        if self.action and not self.grant_id:
            raise ValueError("Action-specific authority requires a grant_id")
        if self.grantor and self.grantor == self.identity:
            raise ValueError("An authority holder cannot grant authority to itself")
        for value, name in ((self.valid_from, "valid_from"), (self.valid_until, "valid_until")):
            if value:
                try:
                    datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError as exc:
                    raise ValueError(f"{name} must be ISO-8601") from exc

    def is_valid_now(self, *, now: datetime | None = None) -> bool:
        if self.revoked:
            return False
        instant = now or datetime.now(timezone.utc)
        if self.valid_from and instant < datetime.fromisoformat(self.valid_from.replace("Z", "+00:00")):
            return False
        if self.valid_until and instant > datetime.fromisoformat(self.valid_until.replace("Z", "+00:00")):
            return False
        return True

    def permits(self, *, action: str, evidence_type: str = "", domain: str = "", method: str = "") -> bool:
        if self.action not in {action, "*"}:
            return False
        for granted, requested in (
            (self.evidence_type, evidence_type),
            (self.domain, domain),
            (self.method, method),
        ):
            if granted and granted != "*" and granted != requested:
                return False
        return True
