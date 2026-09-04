import pytest

from lat_ces.structural.role_handover import (
    ExecutionRole,
    HealthState,
    RecoveryCheckpoint,
    ROMCoordinator,
)
from lat_ces.structural.smc_selector import CandidateRecord, CandidateState, SMCROMSelector
from lat_ces.structural.smc_takeover import SelectionCandidate, select_takeover_candidate


def candidate(candidate_id: str, role: ExecutionRole, *, applicable: bool = True, contract: bool = True) -> SelectionCandidate:
    return SelectionCandidate(
        role_name=role.value,
        evidence=CandidateRecord(
            candidate_id,
            "1.0",
            applicable,
            contract,
            f"registry/{candidate_id}",
        ),
    )


def test_rom_takeover_signal_selects_eligible_recipient_candidate() -> None:
    checkpoint = RecoveryCheckpoint("rev-100", "sha256:100", "verification/rev-100")
    signal = ROMCoordinator(ExecutionRole.PROCESS, checkpoint).observe_failure(HealthState.UNAVAILABLE)

    selector = SMCROMSelector()
    decision = select_takeover_candidate(
        selector,
        signal,
        (
            candidate("wrong-role", ExecutionRole.PROCESS),
            candidate("replacement", ExecutionRole.REVISION_RECOVERY),
        ),
    )

    assert decision.candidate_id == "replacement"
    assert decision.resulting_state is CandidateState.ACTIVE
    assert selector.active_candidate_id == "replacement"


def test_ineligible_recipient_candidate_is_skipped() -> None:
    checkpoint = RecoveryCheckpoint("rev-101", "sha256:101", "verification/rev-101")
    signal = ROMCoordinator(ExecutionRole.PROCESS, checkpoint).observe_failure(HealthState.DEGRADED)
    selector = SMCROMSelector()

    decision = select_takeover_candidate(
        selector,
        signal,
        (
            candidate("bad", ExecutionRole.REVISION_RECOVERY, contract=False),
            candidate("good", ExecutionRole.REVISION_RECOVERY),
        ),
    )

    assert decision.candidate_id == "good"
    assert selector.active_candidate_id == "good"


def test_takeover_fails_when_no_recipient_candidate_exists() -> None:
    checkpoint = RecoveryCheckpoint("rev-102", "sha256:102", "verification/rev-102")
    signal = ROMCoordinator(ExecutionRole.PROCESS, checkpoint).observe_failure(HealthState.DEGRADED)
    selector = SMCROMSelector()

    with pytest.raises(ValueError, match="no candidate available for takeover role"):
        select_takeover_candidate(selector, signal, (candidate("other", ExecutionRole.PROCESS),))


def test_takeover_fails_when_all_matching_candidates_are_ineligible() -> None:
    checkpoint = RecoveryCheckpoint("rev-103", "sha256:103", "verification/rev-103")
    signal = ROMCoordinator(ExecutionRole.REVISION_RECOVERY, checkpoint).observe_failure(HealthState.UNAVAILABLE)
    selector = SMCROMSelector()

    with pytest.raises(ValueError, match="no eligible candidate available for takeover role"):
        select_takeover_candidate(
            selector,
            signal,
            (
                candidate("bad-1", ExecutionRole.PROCESS, applicable=False),
                candidate("bad-2", ExecutionRole.PROCESS, contract=False),
            ),
        )


def test_selector_boundary_remains_model_free() -> None:
    checkpoint = RecoveryCheckpoint("rev-104", "sha256:104", "verification/rev-104")
    signal = ROMCoordinator(ExecutionRole.PROCESS, checkpoint).observe_failure(HealthState.DEGRADED)
    selector = SMCROMSelector()
    entry = candidate("replacement", ExecutionRole.REVISION_RECOVERY)

    select_takeover_candidate(selector, signal, (entry,))

    assert not hasattr(selector, "model")
    assert not hasattr(entry.evidence, "model")
    assert not hasattr(entry.evidence, "peer_model")
