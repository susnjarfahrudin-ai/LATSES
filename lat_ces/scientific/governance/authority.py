from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Authority:
    """Immutable authority grant descriptor.

    The descriptor itself is not proof of authority. CanonicalAuthorityRegistry
    is the only source used to establish a lawful authority chain.
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
    parent_grant_id: str = ""
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
        if self.action and self.grant_id and self.grant_id != "ROOT-GRANT" and not self.parent_grant_id:
            raise ValueError("Non-root authority requires a parent grant")
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

    def permits(
        self,
        *,
        action: str,
        evidence_type: str = "",
        domain: str = "",
        method: str = "",
        purpose: str = "",
    ) -> bool:
        if self.action not in {action, "*"}:
            return False
        for granted, requested in (
            (self.evidence_type, evidence_type),
            (self.domain, domain),
            (self.method, method),
            (self.purpose, purpose),
        ):
            if granted and granted != "*" and granted != requested:
                return False
        return True


class CanonicalAuthorityRegistry:
    """Canonical in-memory trust anchor and authority registry."""

    ROOT_ID = "LAT-CONSTITUTION-ROOT"
    ROOT_GRANT_ID = "ROOT-GRANT"
    GRANT_ACTION = "GRANT_VERIFICATION_AUTHORITY"

    def __init__(self) -> None:
        self._authorities: dict[str, Authority] = {}
        self._revoked_grants: set[str] = set()
        root = Authority(
            identity=self.ROOT_ID,
            level=3,
            scope="*",
            action=self.GRANT_ACTION,
            grant_id=self.ROOT_GRANT_ID,
        )
        self._authorities[root.grant_id] = root
        self._root = root

    @property
    def root(self) -> Authority:
        return self._root

    def get(self, grant_id: str) -> Authority | None:
        return self._authorities.get(grant_id)

    def is_registered(self, authority: Authority) -> bool:
        registered = self._authorities.get(authority.grant_id)
        return registered is authority

    def revoke(self, grant_id: str) -> Authority:
        authority = self._authorities.get(grant_id)
        if authority is None:
            raise KeyError(grant_id)
        if grant_id == self.ROOT_GRANT_ID:
            raise PermissionError("Canonical root authority cannot be revoked")
        self._revoked_grants.add(grant_id)
        return authority

    def is_revoked(self, grant_id: str) -> bool:
        return grant_id in self._revoked_grants

    def register(self, authority: Authority) -> Authority:
        if authority.grant_id == self.ROOT_GRANT_ID:
            raise PermissionError("Canonical root authority cannot be replaced")
        if authority.grant_id in self._authorities:
            raise ValueError(f"Duplicate authority grant: {authority.grant_id}")
        parent = self._authorities.get(authority.parent_grant_id)
        if parent is None:
            raise PermissionError("Authority parent grant is not registered")
        if self.is_revoked(parent.grant_id):
            raise PermissionError("Authority parent cannot issue grants")
        if authority.grantor != parent.identity:
            raise PermissionError("Authority grantor does not match its parent authority")
        if parent.action != self.GRANT_ACTION or not parent.is_valid_now():
            raise PermissionError("Authority parent cannot issue grants")
        self._authorities[authority.grant_id] = authority
        return authority

    def validate_chain(self, grant_id: str) -> tuple[Authority, ...]:
        chain: list[Authority] = []
        seen: set[str] = set()
        current_id = grant_id
        while current_id:
            if current_id in seen:
                raise PermissionError("Authority chain cycle detected")
            seen.add(current_id)
            current = self._authorities.get(current_id)
            if current is None:
                raise PermissionError("Authority chain contains an unknown grant")
            if self.is_revoked(current.grant_id) or not current.is_valid_now():
                raise PermissionError("Authority chain contains an expired or revoked grant")
            chain.append(current)
            if current.grant_id == self.ROOT_GRANT_ID:
                if (
                    current.identity != self.ROOT_ID
                    or current.action != self.GRANT_ACTION
                    or current.level != 3
                    or current.scope != "*"
                    or current.parent_grant_id
                    or current.grantor
                ):
                    raise PermissionError("Canonical root authority is invalid")
                return tuple(chain)
            parent = self._authorities.get(current.parent_grant_id)
            if parent is None:
                raise PermissionError("Authority chain cannot resolve its parent grant")
            if current.grantor != parent.identity:
                raise PermissionError("Authority chain grantor/parent binding is invalid")
            if parent.action != self.GRANT_ACTION:
                raise PermissionError("Authority chain parent is not a grant authority")
            current_id = current.parent_grant_id
        raise PermissionError("Authority chain does not terminate at the canonical root")
