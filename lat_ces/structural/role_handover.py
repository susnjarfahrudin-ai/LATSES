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
    """Deterministic coordinator state for active-role takeover and recovery."""

    state: RecoveryState = RecoveryState.ACTIVE
    active_role: ExecutionRole = ExecutionRole.PROCESS
    recovering_role: ExecutionRole | None = None
    checkpoint: RecoveryCheckpoint | None = None

    def on_failure(self, health: HealthState) -> "RecoveryStateMachine":
        """Move the active role to TAKEOVER and identify only the standby role."""
        if self.state is not RecoveryState.ACTIVE:
            raise ValueError("failure can only be handled from ACTIVE")
        if health is HealthState.HEALTHY:
            raise ValueError("healthy role cannot trigger takeover")
        return RecoveryStateMachine(
            state=RecoveryState.TAKEOVER,
            active_role=self.active_role,
            recovering_role=self.recovering_role or self._other_role(self.active_role),
            checkpoint=self.checkpoint,
        )

    def activate_standby(self) -> "RecoveryStateMachine":
        """Make the standby role active while the failed role becomes recoverable."""
        if self.state is not RecoveryState.TAKEOVER:
            raise ValueError("standby activation requires TAKEOVER state")
        if self.recovering_role is None:
            raise ValueError("TAKEOVER requires a standby role")
        return RecoveryStateMachine(
            state=RecoveryState.ACTIVE,
            active_role=self.recovering_role,
            recovering_role=self.active_role,
            checkpoint=self.checkpoint,
        )

    def begin_recovery(self, checkpoint: RecoveryCheckpoint) -> "RecoveryStateMachine":
        """Recover the inactive role while the newly activated role remains active."""
        if self.state is not RecoveryState.ACTIVE:
            raise ValueError("recovery can begin only while a role is ACTIVE")
        if self.recovering_role is None:
            raise ValueError("recovery requires an inactive role")
        return RecoveryStateMachine(
            state=RecoveryState.RECOVERING,
            active_role=self.active_role,
            recovering_role=self.recovering_role,
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
            active_role=self.active_role,
            recovering_role=self.recovering_role,
            checkpoint=self.checkpoint,
        )

    def mark_ready(self) -> "RecoveryStateMachine":
        """Mark the recovered standby role ready for a future takeover."""
        if self.state is not RecoveryState.CHECKPOINT_VERIFIED:
            raise ValueError("READY requires a verified checkpoint")
        if self.recovering_role is None:
            raise ValueError("READY requires an inactive recovered role")
        return RecoveryStateMachine(
            state=RecoveryState.READY,
            active_role=self.active_role,
            recovering_role=self.recovering_role,
            checkpoint=self.checkpoint,
        )

    @staticmethod
    def _other_role(role: ExecutionRole) -> ExecutionRole:
        return (
            ExecutionRole.REVISION_RECOVERY
            if role is ExecutionRole.PROCESS
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
