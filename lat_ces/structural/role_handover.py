"""Neutral role, takeover, recovery, and state-machine contracts.

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


class RecoveryState(str, Enum):
    """Lifecycle states for controlled takeover and recovery."""

    ACTIVE = "ACTIVE"
    TAKEOVER = "TAKEOVER"
    STANDBY = "STANDBY"
    RECOVERING = "RECOVERING"
    CHECKPOINT_VERIFIED = "CHECKPOINT_VERIFIED"
    READY = "READY"


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


@dataclass(frozen=True)
class RecoveryStateMachine:
    """Small deterministic state machine for takeover and recovery."""

    state: RecoveryState = RecoveryState.ACTIVE
    role: ExecutionRole = ExecutionRole.PROCESS
    checkpoint: RecoveryCheckpoint | None = None

    def on_failure(self, health: HealthState) -> "RecoveryStateMachine":
        """Enter TAKEOVER only for an observed degraded/unavailable active role."""
        if self.state is not RecoveryState.ACTIVE:
            raise ValueError("failure can only be handled from ACTIVE")
        if health is HealthState.HEALTHY:
            raise ValueError("healthy role cannot trigger takeover")
        return RecoveryStateMachine(
            state=RecoveryState.TAKEOVER,
            role=self.role,
            checkpoint=self.checkpoint,
        )

    def activate_standby(self) -> "RecoveryStateMachine":
        """Transfer active responsibility to the waiting role without model coupling."""
        if self.state is not RecoveryState.TAKEOVER:
            raise ValueError("standby activation requires TAKEOVER state")
        return RecoveryStateMachine(
            state=RecoveryState.ACTIVE,
            role=self._other_role(),
            checkpoint=self.checkpoint,
        )

    def begin_recovery(self, checkpoint: RecoveryCheckpoint) -> "RecoveryStateMachine":
        """Recover the inactive peer from the supplied verified checkpoint evidence."""
        if self.state is not RecoveryState.ACTIVE:
            raise ValueError("recovery can begin only while a role is ACTIVE")
        return RecoveryStateMachine(
            state=RecoveryState.RECOVERING,
            role=self.role,
            checkpoint=checkpoint,
        )

    def verify_checkpoint(self) -> "RecoveryStateMachine":
        """Accept the recovered state only after a checkpoint exists."""
        if self.state is not RecoveryState.RECOVERING:
            raise ValueError("checkpoint verification requires RECOVERING state")
        if self.checkpoint is None:
            raise ValueError("checkpoint verification requires a recovery checkpoint")
        return RecoveryStateMachine(
            state=RecoveryState.CHECKPOINT_VERIFIED,
            role=self.role,
            checkpoint=self.checkpoint,
        )

    def mark_ready(self) -> "RecoveryStateMachine":
        """Mark the recovered role ready for a future takeover."""
        if self.state is not RecoveryState.CHECKPOINT_VERIFIED:
            raise ValueError("READY requires a verified checkpoint")
        return RecoveryStateMachine(
            state=RecoveryState.READY,
            role=self.role,
            checkpoint=self.checkpoint,
        )

    def _other_role(self) -> ExecutionRole:
        return (
            ExecutionRole.REVISION_RECOVERY
            if self.role is ExecutionRole.PROCESS
            else ExecutionRole.PROCESS
        )


__all__ = [
    "ExecutionRole",
    "HealthState",
    "RecoveryState",
    "RoleHealth",
    "RecoveryCheckpoint",
    "HandoverRequest",
    "HandoverDecision",
    "TakeoverSignal",
    "RecoveryStateMachine",
]
