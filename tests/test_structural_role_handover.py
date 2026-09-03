from dataclasses import FrozenInstanceError, replace

import pytest

from lat_ces.structural.role_handover import (
    ExecutionRole,
    HandoverDecision,
    HandoverRequest,
    HealthState,
    RoleHealth,
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
