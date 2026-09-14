"""Adversarial A/B role-rotation acceptance test.

This test models two isolated execution roles. It never copies a compromised
runtime state into the standby role. Only a verified recovery checkpoint and
verified attack-defense evidence are allowed across the handover boundary.
"""

from dataclasses import dataclass

from lat_ces.structural.role_handover import (
    ExecutionRole,
    HealthState,
    RecoveryCheckpoint,
    RecoveryState,
    RecoveryStateMachine,
    ROMCoordinator,
)
from lat_ces.structural.smc_selector import CandidateRecord, CandidateState, SMCROMSelector
from lat_ces.structural.smc_takeover import SelectionCandidate, select_takeover_candidate


@dataclass(frozen=True)
class AttackEvidence:
    attack_id: str
    attack_path: str
    defense_patch: str
    verification_sha: str


def _candidate(candidate_id: str, role: ExecutionRole) -> SelectionCandidate:
    return SelectionCandidate(
        role_name=role.value,
        evidence=CandidateRecord(
            candidate_id,
            "verified-1",
            True,
            True,
            f"verification/{candidate_id}",
        ),
    )


def test_adversarial_two_process_learning_and_role_rotation_cycle() -> None:
    """A is attacked, B learns and takes over, then B is attacked and A recovers.

    The assertions intentionally prove the invariants:
    * roles remain distinct;
    * the compromised role never becomes the immediate takeover target;
    * takeover starts from the last verified checkpoint;
    * the standby role is independently selected and promoted;
    * recovery returns the failed role to READY rather than ACTIVE;
    * the same cycle works in the opposite direction.
    """
    baseline = RecoveryCheckpoint(
        "baseline-001",
        "sha256:last-known-good",
        "verification/baseline-001",
    )

    # --- Round 1: A/PROCESS is attacked; B/REVISION_RECOVERY takes over.
    a = RecoveryStateMachine(active_role=ExecutionRole.PROCESS, checkpoint=baseline)
    b_selector = SMCROMSelector()

    attack_a = AttackEvidence(
        "attack-A-001",
        "ipc/replay-capacity",
        "defense/replay-boundary-v2",
        "sha256:defense-A-001",
    )

    takeover = a.on_failure(HealthState.DEGRADED)
    assert takeover.state is RecoveryState.TAKEOVER
    assert takeover.recovering_role is ExecutionRole.REVISION_RECOVERY
    assert takeover.active_role is not takeover.recovering_role

    signal = ROMCoordinator(
        ExecutionRole.PROCESS,
        baseline,
    ).observe_failure(HealthState.DEGRADED)
    assert signal.recipient_role is ExecutionRole.REVISION_RECOVERY
    assert signal.checkpoint is baseline

    decision = select_takeover_candidate(
        b_selector,
        signal,
        (_candidate("B-001", ExecutionRole.REVISION_RECOVERY),),
    )
    assert decision.resulting_state is CandidateState.ACTIVE
    assert b_selector.active_candidate_id == "B-001"

    # B prepares a defense from attack evidence, but receives no compromised A
    # implementation/state.
    b_checkpoint = RecoveryCheckpoint(
        "B-prepared-A-001",
        attack_a.verification_sha,
        "verification/B-prepared-A-001",
    )
    b_active = takeover.activate_standby().promote_standby()
    b_recovery = b_active.begin_recovery(b_checkpoint).verify_checkpoint().mark_ready()

    assert b_active.active_role is ExecutionRole.REVISION_RECOVERY
    assert b_active.recovering_role is ExecutionRole.PROCESS
    assert b_recovery.state is RecoveryState.READY
    assert b_recovery.recovering_role is ExecutionRole.PROCESS
    assert b_recovery.checkpoint is b_checkpoint

    # --- Round 2: B is now ACTIVE and is attacked; A takes over.
    b_runtime = RecoveryStateMachine(
        active_role=ExecutionRole.REVISION_RECOVERY,
        checkpoint=b_checkpoint,
    )
    a_selector = SMCROMSelector()

    attack_b = AttackEvidence(
        "attack-B-001",
        "flowguard/frequency-volume-concurrency-novelty",
        "defense/flowguard-v3",
        "sha256:defense-B-001",
    )

    takeover_b = b_runtime.on_failure(HealthState.UNAVAILABLE)
    assert takeover_b.state is RecoveryState.TAKEOVER
    assert takeover_b.recovering_role is ExecutionRole.PROCESS

    signal_b = ROMCoordinator(
        ExecutionRole.REVISION_RECOVERY,
        b_checkpoint,
    ).observe_failure(HealthState.UNAVAILABLE)
    assert signal_b.recipient_role is ExecutionRole.PROCESS
    assert signal_b.checkpoint is b_checkpoint

    decision_a = select_takeover_candidate(
        a_selector,
        signal_b,
        (_candidate("A-002", ExecutionRole.PROCESS),),
    )
    assert decision_a.resulting_state is CandidateState.ACTIVE
    assert a_selector.active_candidate_id == "A-002"

    # A becomes active, while B is recovered from its last verified checkpoint.
    a_active = takeover_b.activate_standby().promote_standby()
    a_recovery = (
        a_active
        .begin_recovery(
            RecoveryCheckpoint(
                "A-prepared-B-001",
                attack_b.verification_sha,
                "verification/A-prepared-B-001",
            )
        )
        .verify_checkpoint()
        .mark_ready()
    )

    assert a_active.active_role is ExecutionRole.PROCESS
    assert a_active.recovering_role is ExecutionRole.REVISION_RECOVERY
    assert a_recovery.state is RecoveryState.READY
    assert a_recovery.recovering_role is ExecutionRole.REVISION_RECOVERY

    # The learning loop preserves separation: each round produces evidence
    # and a verified defense, not a peer runtime/model copy.
    assert attack_a.attack_id != attack_b.attack_id
    assert attack_a.verification_sha != attack_b.verification_sha
    assert not hasattr(signal, "peer_model")
    assert not hasattr(signal_b, "peer_model")
