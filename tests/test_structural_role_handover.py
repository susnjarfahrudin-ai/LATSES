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
    RoleHealth,
    TakeoverSignal,
)


def test_process_role_operates_independently() -> None:
    health = RoleHealth(
        role=ExecutionRole.PROCESS,
        state=HealthState.HEALTHY,
        revision_id="rev-001",
        provenance="process/run-001",
    )

    assert health.role is ExecutionRole.PROCESS
    assert health.state is HealthState.HEALTHY


def test_revision_recovery_role_operates_independently() -> None:
    health = RoleHealth(
        role=ExecutionRole.REVISION_RECOVERY,
        state=HealthState.HEALTHY,
        revision_id="rev-002",
        provenance="recovery/checkpoint-001",
    )

    assert health.role is ExecutionRole.REVISION_RECOVERY
    assert health.state is HealthState.HEALTHY


def test_process_to_revision_recovery_handover() -> None:
    request = HandoverRequest(
        from_role=ExecutionRole.PROCESS,
        to_role=ExecutionRole.REVISION_RECOVERY,
        reason=HealthState.DEGRADED,
        revision_id="rev-003",
        content_hash="sha256:abc",
        provenance="process/health-check",
    )
    decision = HandoverDecision(
        request=request,
        accepted=True,
        target_revision_id="rev-003",
    )

    assert decision.request.from_role is ExecutionRole.PROCESS
    assert decision.request.to_role is ExecutionRole.REVISION_RECOVERY
    assert decision.target_revision_id == "rev-003"


def test_revision_recovery_to_process_handover() -> None:
    request = HandoverRequest(
        from_role=ExecutionRole.REVISION_RECOVERY,
        to_role=ExecutionRole.PROCESS,
        reason=HealthState.UNAVAILABLE,
        revision_id="rev-004",
        content_hash="sha256:def",
        provenance="recovery/health-check",
    )
    decision = HandoverDecision(
        request=request,
        accepted=True,
        target_revision_id="rev-004",
    )

    assert decision.request.from_role is ExecutionRole.REVISION_RECOVERY
    assert decision.request.to_role is ExecutionRole.PROCESS


def test_healthy_role_cannot_request_handover() -> None:
    with pytest.raises(ValueError, match="healthy role does not justify handover"):
        HandoverRequest(
            from_role=ExecutionRole.PROCESS,
            to_role=ExecutionRole.REVISION_RECOVERY,
            reason=HealthState.HEALTHY,
            revision_id="rev-005",
            content_hash="sha256:ghi",
            provenance="process/health-check",
        )


def test_handover_preserves_identity_and_is_immutable() -> None:
    request = HandoverRequest(
        from_role=ExecutionRole.PROCESS,
        to_role=ExecutionRole.REVISION_RECOVERY,
        reason=HealthState.UNAVAILABLE,
        revision_id="rev-006",
        content_hash="sha256:jkl",
        provenance="process/health-check",
    )
    decision = HandoverDecision(
        request=request,
        accepted=True,
        target_revision_id="rev-006",
    )

    assert decision.request.revision_id == "rev-006"
    assert replace(request, provenance="handover/reissued").revision_id == request.revision_id
    with pytest.raises(FrozenInstanceError):
        request.revision_id = "rev-other"  # type: ignore[misc]


def test_accepted_handover_cannot_change_revision_identity() -> None:
    request = HandoverRequest(
        from_role=ExecutionRole.PROCESS,
        to_role=ExecutionRole.REVISION_RECOVERY,
        reason=HealthState.DEGRADED,
        revision_id="rev-007",
        content_hash="sha256:mno",
        provenance="process/health-check",
    )

    with pytest.raises(ValueError, match="must preserve revision identity"):
        HandoverDecision(
            request=request,
            accepted=True,
            target_revision_id="rev-other",
        )


def test_takeover_signal_is_role_local_and_carries_last_verified_checkpoint() -> None:
    checkpoint = RecoveryCheckpoint(
        revision_id="rev-008",
        content_hash="sha256:pqr",
        provenance="verification/checkpoint-008",
    )
    signal = TakeoverSignal(
        recipient_role=ExecutionRole.REVISION_RECOVERY,
        cause=HealthState.UNAVAILABLE,
        checkpoint=checkpoint,
        provenance="coordinator/health-event",
    )

    assert signal.recipient_role is ExecutionRole.REVISION_RECOVERY
    assert signal.cause is HealthState.UNAVAILABLE
    assert signal.checkpoint.revision_id == "rev-008"
    assert not hasattr(signal, "from_role")
    assert not hasattr(signal, "peer_model")


def test_recovery_checkpoint_is_immutable() -> None:
    checkpoint = RecoveryCheckpoint(
        revision_id="rev-009",
        content_hash="sha256:stu",
        provenance="verification/checkpoint-009",
    )

    with pytest.raises(FrozenInstanceError):
        checkpoint.content_hash = "sha256:changed"  # type: ignore[misc]


def test_takeover_signal_requires_failure_or_degradation() -> None:
    checkpoint = RecoveryCheckpoint(
        revision_id="rev-010",
        content_hash="sha256:vwx",
        provenance="verification/checkpoint-010",
    )

    with pytest.raises(ValueError, match="cannot trigger takeover"):
        TakeoverSignal(
            recipient_role=ExecutionRole.PROCESS,
            cause=HealthState.HEALTHY,
            checkpoint=checkpoint,
            provenance="coordinator/health-event",
        )


def test_process_failure_takeover_standby_activation_and_recovery() -> None:
    checkpoint = RecoveryCheckpoint(
        revision_id="rev-011",
        content_hash="sha256:yz0",
        provenance="verification/checkpoint-011",
    )
    process = RecoveryStateMachine(active_role=ExecutionRole.PROCESS)

    takeover = process.on_failure(HealthState.DEGRADED)
    standby = takeover.activate_standby()
    active_recovery = standby.promote_standby()
    recovering = active_recovery.begin_recovery(checkpoint)
    verified = recovering.verify_checkpoint()
    ready = verified.mark_ready()

    assert takeover.state is RecoveryState.TAKEOVER
    assert standby.state is RecoveryState.STANDBY
    assert standby.active_role is ExecutionRole.PROCESS
    assert standby.recovering_role is ExecutionRole.REVISION_RECOVERY
    assert active_recovery.state is RecoveryState.ACTIVE
    assert active_recovery.active_role is ExecutionRole.REVISION_RECOVERY
    assert active_recovery.recovering_role is ExecutionRole.PROCESS
    assert recovering.state is RecoveryState.RECOVERING
    assert recovering.active_role is ExecutionRole.REVISION_RECOVERY
    assert recovering.recovering_role is ExecutionRole.PROCESS
    assert verified.state is RecoveryState.CHECKPOINT_VERIFIED
    assert ready.state is RecoveryState.READY
    assert ready.active_role is ExecutionRole.REVISION_RECOVERY
    assert ready.recovering_role is ExecutionRole.PROCESS
    assert ready.checkpoint is checkpoint


def test_recovery_role_can_take_over_back_and_recover_again() -> None:
    checkpoint = RecoveryCheckpoint(
        revision_id="rev-012",
        content_hash="sha256:abc2",
        provenance="verification/checkpoint-012",
    )
    recovery = RecoveryStateMachine(
        active_role=ExecutionRole.REVISION_RECOVERY,
        checkpoint=checkpoint,
    )

    takeover = recovery.on_failure(HealthState.UNAVAILABLE)
    standby = takeover.activate_standby()
    active_process = standby.promote_standby()
    recovering = active_process.begin_recovery(checkpoint)
    ready = recovering.verify_checkpoint().mark_ready()

    assert standby.state is RecoveryState.STANDBY
    assert active_process.active_role is ExecutionRole.PROCESS
    assert active_process.recovering_role is ExecutionRole.REVISION_RECOVERY
    assert ready.active_role is ExecutionRole.PROCESS
    assert ready.recovering_role is ExecutionRole.REVISION_RECOVERY
    assert ready.state is RecoveryState.READY
    assert ready.checkpoint is checkpoint


def test_state_machine_can_run_a_second_takeover_after_recovery() -> None:
    checkpoint = RecoveryCheckpoint(
        revision_id="rev-013",
        content_hash="sha256:next",
        provenance="verification/checkpoint-013",
    )
    first = RecoveryStateMachine(active_role=ExecutionRole.PROCESS)
    ready = (
        first.on_failure(HealthState.DEGRADED)
        .activate_standby()
        .promote_standby()
        .begin_recovery(checkpoint)
        .verify_checkpoint()
        .mark_ready()
    )

    second_takeover = ready.on_failure(HealthState.UNAVAILABLE)
    second_standby = second_takeover.activate_standby()
    second_active = second_standby.promote_standby()

    assert second_takeover.state is RecoveryState.TAKEOVER
    assert second_standby.state is RecoveryState.STANDBY
    assert second_active.state is RecoveryState.ACTIVE
    assert second_active.active_role is ExecutionRole.PROCESS
    assert second_active.recovering_role is ExecutionRole.REVISION_RECOVERY


def test_state_machine_rejects_invalid_transition() -> None:
    machine = RecoveryStateMachine()

    with pytest.raises(ValueError, match="standby activation requires TAKEOVER state"):
        machine.activate_standby()

    with pytest.raises(ValueError, match="healthy role cannot trigger takeover"):
        machine.on_failure(HealthState.HEALTHY)

    with pytest.raises(ValueError, match="standby promotion requires STANDBY state"):
        machine.promote_standby()


def test_ready_requires_verified_checkpoint() -> None:
    machine = RecoveryStateMachine(state=RecoveryState.RECOVERING)

    with pytest.raises(ValueError, match="checkpoint verification requires a recovery checkpoint"):
        machine.verify_checkpoint()
