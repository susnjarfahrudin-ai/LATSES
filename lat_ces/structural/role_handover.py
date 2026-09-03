"""Neutral role and handover contracts for independent structural execution paths.

The PROCESS and REVISION_RECOVERY roles are peers. This module contains no
implementation dependency on either BuildingModel implementation; it only
carries immutable identity, health, provenance, and handover evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExecutionRole(str, Enum):
    """Independent execution roles that may become active."""

    PROCESS = "PROCESS"
    REVISION_RECOVERY = "REVISION_RECOVERY"


class HealthState(str, Enum):
    """Operational health used to justify an explicit handover."""

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
class HandoverRequest:
    """Immutable request to transfer active responsibility between peer roles."""

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
    """Immutable decision acknowledging the target role takeover."""

    request: HandoverRequest
    accepted: bool
    target_revision_id: str

    def __post_init__(self) -> None:
        if self.accepted and self.target_revision_id != self.request.revision_id:
            raise ValueError("accepted handover must preserve revision identity")


__all__ = [
    "ExecutionRole",
    "HealthState",
    "RoleHealth",
    "HandoverRequest",
    "HandoverDecision",
]
