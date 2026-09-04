from dataclasses import FrozenInstanceError, replace

import pytest

from lat_ces.structural.role_handover import (
    ExecutionRole,
    HandoverDecision,
    HandoverRequest,
    HealthState,
    RecoveryCheckpoint,
    RecoveryState,
    RecoveryStateMachine,
    ROMCoordinator,
    RoleHealth,
    TakeoverSignal,
)


def test_process_role_operates_independently() -> None:
    health = RoleHealth(ExecutionRole.PROCESS, HealthState.HEALTHY, "rev-001", "process/run-001")
    assert health.role is ExecutionRole.PROCESS
    assert health.state is HealthState.HEALTHY


def test_revision_recovery_role_operates_independently() -> None:
    health = RoleHealth(
        ExecutionRole.REVISION_RECOVERY,
        HealthState.HEALTHY,
        "rev-002",
        "recovery/checkpoint-001",
    )
    assert health.role is ExecutionRole.REVISION_RECOVERY
    assert health.state is HealthState.HEALTHY


def test_process_to_revision_recovery_handover() -> None:
    request = HandoverRequest(ExecutionRole.PROCESS, ExecutionRole.REVISION_RECOVERY, HealthState.DEGRADED, "rev-003", "sha256:abc", "process/health-check")
    decision = HandoverDecision(request, True, "rev-003")
    assert decision.request.to_role is ExecutionRole.REVISION_RECOVERY
    assert decision.target_revision_id == "rev-003"


def test_revision_recovery_to_process_handover() -> None:
    request = HandoverRequest(ExecutionRole.REVISION_RECOVERY, ExecutionRole.PROCESS, HealthState.UNAVAILABLE, "rev-004", "sha256:def", "recovery/health-check")
    decision = HandoverDecision(request, True, "rev-004")
    assert decision.request.to_role is ExecutionRole.PROCESS


def test_healthy_role_cannot_request_handover() -> None:
    with pytest.raises(ValueError, match="healthy role does not justify handover"):
        HandoverRequest(ExecutionRole.PROCESS, ExecutionRole.REVISION_RECOVERY, HealthState.HEALTHY, "rev-005", "sha256:ghi", "process/health-check")


def test_handover_preserves_identity_and_is_immutable() -> None:
    request = HandoverRequest(ExecutionRole.PROCESS, ExecutionRole.REVISION_RECOVERY, HealthState.UNAVAILABLE, "rev-006", "sha256:jkl", "process/health-check")
    decision = HandoverDecision(request, True, "rev-006")
    assert decision.request.revision_id == "rev-006"
    assert replace(request, provenance="handover/reissued").revision_id == request.revision_id
    with pytest.raises(FrozenInstanceError):
        request.revision_id = "rev-other"  # type: ignore[misc]


def test_accepted_handover_cannot_change_revision_identity() -> None:
    request = HandoverRequest(ExecutionRole.PROCESS, ExecutionRole.REVISION_RECOVERY, HealthState.DEGRADED, "rev-007", "sha256:mno", "process/health-check")
    with pytest.raises(ValueError, match="must preserve revision identity"):
        HandoverDecision(request, True, "rev-other")


def test_takeover_signal_is_role_local_and_carries_last_verified_checkpoint() -> None:
    checkpoint = RecoveryCheckpoint("rev-008", "sha256:pqr", "verification/checkpoint-008")
    signal = TakeoverSignal(ExecutionRole.REVISION_RECOVERY, HealthState.UNAVAILABLE, checkpoint, "coordinator/health-event")
    assert signal.recipient_role is ExecutionRole.REVISION_RECOVERY
    assert signal.checkpoint.revision_id == "rev-008"
    assert not hasattr(signal, "from_role")
    assert not hasattr(signal, "peer_model")


def test_recovery_checkpoint_is_immutable() -> None:
    checkpoint = RecoveryCheckpoint("rev-009", "sha256:stu", "verification/checkpoint-009")
    with pytest.raises(FrozenInstanceError):
        checkpoint.content_hash = "sha256:changed"  # type: ignore[misc]


def test_takeover_signal_requires_failure_or_degradation() -> None:
    checkpoint = RecoveryCheckpoint("rev-010", "sha256:vwx", "verification/checkpoint-010")
    with pytest.raises(ValueError, match="cannot trigger takeover"):
        TakeoverSignal(ExecutionRole.PROCESS, HealthState.HEALTHY, checkpoint, "coordinator/health-event")


def test_process_failure_takeover_and_recovery_cycle() -> None:
    checkpoint = RecoveryCheckpoint("rev-011", "sha256:yz0", "verification/checkpoint-011")
    process = RecoveryStateMachine(active_role=ExecutionRole.PROCESS)
    takeover = process.on_failure(HealthState.DEGRADED)
    standby = takeover.activate_standby()
    active_recovery = standby.promote_standby()
    recovering = active_recovery.begin_recovery(checkpoint)
    verified = recovering.verify_checkpoint()
    ready = verified.mark_ready()

    assert takeover.state is RecoveryState.TAKEOVER
    assert standby.state is RecoveryState.STANDBY
    assert active_recovery.state is RecoveryState.ACTIVE
    assert active_recovery.active_role is ExecutionRole.REVISION_RECOVERY
    assert recovering.state is RecoveryState.RECOVERING
    assert verified.state is RecoveryState.CHECKPOINT_VERIFIED
    assert ready.state is RecoveryState.READY
    assert ready.recovering_role is ExecutionRole.PROCESS
    assert ready.checkpoint is checkpoint


def test_recovery_role_can_take_over_back_and_recover_again() -> None:
    checkpoint = RecoveryCheckpoint("rev-012", "sha256:abc2", "verification/checkpoint-012")
    recovery = RecoveryStateMachine(active_role=ExecutionRole.REVISION_RECOVERY, checkpoint=checkpoint)
    takeover = recovery.on_failure(HealthState.UNAVAILABLE)
    active_process = takeover.activate_standby().promote_standby()
    ready = active_process.begin_recovery(checkpoint).verify_checkpoint().mark_ready()
    assert active_process.active_role is ExecutionRole.PROCESS
    assert ready.recovering_role is ExecutionRole.REVISION_RECOVERY
    assert ready.state is RecoveryState.READY


def test_state_machine_rejects_invalid_transition() -> None:
    machine = RecoveryStateMachine()
    with pytest.raises(ValueError, match="standby activation requires TAKEOVER state"):
        machine.activate_standby()
    with pytest.raises(ValueError, match="healthy role cannot trigger takeover"):
        machine.on_failure(HealthState.HEALTHY)


def test_ready_requires_verified_checkpoint() -> None:
    machine = RecoveryStateMachine(state=RecoveryState.RECOVERING)
    with pytest.raises(ValueError, match="checkpoint verification requires a recovery checkpoint"):
        machine.verify_checkpoint()


def test_rom_is_model_free_and_emits_role_local_takeover_signal() -> None:
    checkpoint = RecoveryCheckpoint("rev-rom", "sha256:rom", "verification/rom")
    rom = ROMCoordinator(ExecutionRole.PROCESS, checkpoint)
    signal = rom.observe_failure(HealthState.DEGRADED)
    assert signal.recipient_role is ExecutionRole.REVISION_RECOVERY
    assert signal.checkpoint is checkpoint
    assert not hasattr(rom, "model")
    assert not hasattr(rom, "peer_model")
    with pytest.raises(FrozenInstanceError):
        rom.active_role = ExecutionRole.REVISION_RECOVERY  # type: ignore[misc]


def test_rom_does_not_trigger_takeover_from_healthy_state() -> None:
    rom = ROMCoordinator(ExecutionRole.PROCESS, RecoveryCheckpoint("rev-rom-2", "sha256:rom2", "verification/rom2"))
    with pytest.raises(ValueError, match="cannot trigger takeover"):
        rom.observe_failure(HealthState.HEALTHY)
