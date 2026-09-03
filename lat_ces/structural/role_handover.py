"""Neutral role, takeover, and recovery contracts for independent execution paths.

PROCESS and REVISION_RECOVERY remain implementation-isolated. The neutral
contracts may be used by a coordinator, but a role-local signal intentionally
does not disclose the peer model or its implementation identity.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExecutionRole(str, Enum):
    """Independent execution roles that may become active."""

    PROCESS = "PROCESS"
    REVISION_RECOVERY = "REVISION_RECOVERY"


class HealthState(str, Enum):
    """Operational health used to justify an explicit takeover."""

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class RoleHealth:
    """Immutable health evidence for one execution role."""

    role: ExecutionRole
    state: HealthState
    revision_id: str
    provenance: str


@dataclass(frozen=True)
class RecoveryCheckpoint:
    """Last verified state from which an inactive role can recover."""

    revision_id: str
    content_hash: str
    provenance: str

    def __post_init__(self) -> None:
        if not self.revision_id:
            raise ValueError("checkpoint revision_id must not be empty")
        if not self.content_hash:
            raise ValueError("checkpoint content_hash must not be empty")
        if not self.provenance:
            raise ValueError("checkpoint provenance must not be empty")


@dataclass(frozen=True)
class HandoverRequest:
    """Immutable coordinator request to transfer active responsibility."""

    from_role: ExecutionRole
    to_role: ExecutionRole
    reason: HealthState
    revision_id: str
    content_hash: str
    provenance: str

    def __post_init__(self) -> None:
        if self.from_role is self.to_role:
            raise ValueError("handover requires distinct source and target roles")
        if self.reason is HealthState.HEALTHY:
            raise ValueError("healthy role does not justify handover")
        if not self.revision_id:
            raise ValueError("revision_id must not be empty")
        if not self.content_hash:
            raise ValueError("content_hash must not be empty")
        if not self.provenance:
            raise ValueError("provenance must not be empty")


@dataclass(frozen=True)
class HandoverDecision:
    """Immutable coordinator decision acknowledging target takeover."""

    request: HandoverRequest
    accepted: bool
    target_revision_id: str

    def __post_init__(self) -> None:
        if self.accepted and self.target_revision_id != self.request.revision_id:
            raise ValueError("accepted handover must preserve revision identity")


@dataclass(frozen=True)
class TakeoverSignal:
    """Role-local activation signal that does not identify the peer model."""

    recipient_role: ExecutionRole
    cause: HealthState
    checkpoint: RecoveryCheckpoint
    provenance: str

    def __post_init__(self) -> None:
        if self.cause is HealthState.HEALTHY:
            raise ValueError("healthy state cannot trigger takeover")
        if not self.provenance:
            raise ValueError("takeover provenance must not be empty")


__all__ = [
    "ExecutionRole",
    "HealthState",
    "RoleHealth",
    "RecoveryCheckpoint",
    "HandoverRequest",
    "HandoverDecision",
    "TakeoverSignal",
]
