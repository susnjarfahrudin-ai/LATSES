"""ROM coordination contracts for isolated PROCESS and REVISION/RECOVERY roles.

The coordinator is read-only with respect to both execution models: it stores
only immutable operational evidence and emits role-local takeover signals.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExecutionRole(str, Enum):
    PROCESS = "PROCESS"
    REVISION_RECOVERY = "REVISION_RECOVERY"


class HealthState(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


class RecoveryState(str, Enum):
    ACTIVE = "ACTIVE"
    TAKEOVER = "TAKEOVER"
    STANDBY = "STANDBY"
    RECOVERING = "RECOVERING"
    CHECKPOINT_VERIFIED = "CHECKPOINT_VERIFIED"
    READY = "READY"


@dataclass(frozen=True)
class RoleHealth:
    role: ExecutionRole
    state: HealthState
    revision_id: str
    provenance: str


@dataclass(frozen=True)
class RecoveryCheckpoint:
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
    request: HandoverRequest
    accepted: bool
    target_revision_id: str

    def __post_init__(self) -> None:
        if self.accepted and self.target_revision_id != self.request.revision_id:
            raise ValueError("accepted handover must preserve revision identity")


@dataclass(frozen=True)
class TakeoverSignal:
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
    state: RecoveryState = RecoveryState.ACTIVE
    active_role: ExecutionRole = ExecutionRole.PROCESS
    recovering_role: ExecutionRole | None = None
    checkpoint: RecoveryCheckpoint | None = None

    def on_failure(self, health: HealthState) -> "RecoveryStateMachine":
        if self.state not in {RecoveryState.ACTIVE, RecoveryState.READY}:
            raise ValueError("failure can only be handled from ACTIVE or READY")
        if health is HealthState.HEALTHY:
            raise ValueError("healthy role cannot trigger takeover")
        standby_role = self.recovering_role or self._other_role(self.active_role)
        return RecoveryStateMachine(RecoveryState.TAKEOVER, self.active_role, standby_role, self.checkpoint)

    def activate_standby(self) -> "RecoveryStateMachine":
        if self.state is not RecoveryState.TAKEOVER or self.recovering_role is None:
            raise ValueError("standby activation requires TAKEOVER state")
        return RecoveryStateMachine(RecoveryState.STANDBY, self.active_role, self.recovering_role, self.checkpoint)

    def promote_standby(self) -> "RecoveryStateMachine":
        if self.state is not RecoveryState.STANDBY or self.recovering_role is None:
            raise ValueError("standby promotion requires STANDBY state")
        return RecoveryStateMachine(RecoveryState.ACTIVE, self.recovering_role, self.active_role, self.checkpoint)

    def begin_recovery(self, checkpoint: RecoveryCheckpoint) -> "RecoveryStateMachine":
        if self.state is not RecoveryState.ACTIVE or self.recovering_role is None:
            raise ValueError("recovery can begin only while a role is ACTIVE")
        return RecoveryStateMachine(RecoveryState.RECOVERING, self.active_role, self.recovering_role, checkpoint)

    def verify_checkpoint(self) -> "RecoveryStateMachine":
        if self.state is not RecoveryState.RECOVERING:
            raise ValueError("checkpoint verification requires RECOVERING state")
        if self.checkpoint is None:
            raise ValueError("checkpoint verification requires a recovery checkpoint")
        return RecoveryStateMachine(RecoveryState.CHECKPOINT_VERIFIED, self.active_role, self.recovering_role, self.checkpoint)

    def mark_ready(self) -> "RecoveryStateMachine":
        if self.state is not RecoveryState.CHECKPOINT_VERIFIED or self.recovering_role is None:
            raise ValueError("READY requires a verified checkpoint")
        return RecoveryStateMachine(RecoveryState.READY, self.active_role, self.recovering_role, self.checkpoint)

    @staticmethod
    def _other_role(role: ExecutionRole) -> ExecutionRole:
        return ExecutionRole.REVISION_RECOVERY if role is ExecutionRole.PROCESS else ExecutionRole.PROCESS


@dataclass(frozen=True)
class ROMCoordinator:
    """Read-only monitor/coordinator with no BuildingModel dependency."""

    active_role: ExecutionRole
    last_verified_checkpoint: RecoveryCheckpoint

    def observe_failure(self, health: HealthState) -> TakeoverSignal:
        if health is HealthState.HEALTHY:
            raise ValueError("healthy state cannot trigger takeover")
        recipient = (
            ExecutionRole.REVISION_RECOVERY
            if self.active_role is ExecutionRole.PROCESS
            else ExecutionRole.PROCESS
        )
        return TakeoverSignal(
            recipient_role=recipient,
            cause=health,
            checkpoint=self.last_verified_checkpoint,
            provenance="rom/failure-observation",
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
    "ROMCoordinator",
]
