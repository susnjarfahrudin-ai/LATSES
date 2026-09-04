from dataclasses import FrozenInstanceError

import pytest

from lat_ces.structural.smc_selector import (
    BENCH_CAPACITY,
    CandidateRecord,
    CandidateState,
    SMCROMSelector,
)


def candidate(candidate_id: str, *, applicable: bool = True, contract: bool = True) -> CandidateRecord:
    return CandidateRecord(candidate_id, "1.0", applicable, contract, f"registry/{candidate_id}")


def test_select_accepts_only_eligible_candidate() -> None:
    selector = SMCROMSelector()
    decision = selector.select(candidate("A"))
    assert decision.operation == "select"
    assert decision.resulting_state is CandidateState.ACTIVE
    assert selector.active_candidate_id == "A"


def test_select_rejects_inapplicable_candidate() -> None:
    selector = SMCROMSelector()
    decision = selector.select(candidate("B", applicable=False))
    assert decision.resulting_state is CandidateState.INVALID
    assert selector.active_candidate_id is None
    assert selector.history[-1].operation == "reject"


def test_bench_is_bounded_fifo() -> None:
    selector = SMCROMSelector(bench_capacity=3)
    for item in ("B1", "B2", "B3", "B4"):
        selector.bench(candidate(item))
    assert selector.bench_ids == ("B2", "B3", "B4")
    assert selector.history[-1].operation == "bench"


def test_replace_supersedes_previous_active_without_erasing_history() -> None:
    selector = SMCROMSelector()
    selector.select(candidate("A"))
    decision = selector.replace(candidate("B"))
    assert decision.operation == "replace"
    assert decision.supersedes_candidate_id == "A"
    assert selector.active_candidate_id == "B"
    assert any(item.candidate_id == "A" and item.operation == "select" for item in selector.history)


def test_recover_returns_inactive_candidate_to_bench_not_active() -> None:
    selector = SMCROMSelector()
    selector.select(candidate("A"))
    selector.replace(candidate("B"))
    decision = selector.recover("A", "checkpoint/rev-1")
    assert decision.resulting_state is CandidateState.BENCHED
    assert selector.active_candidate_id == "B"
    assert "A" in selector.bench_ids


def test_reconstruct_restores_bounded_operational_state() -> None:
    selector = SMCROMSelector(bench_capacity=3)
    result = selector.reconstruct(("B", "C"), "A", "restart/session-1")
    assert result.candidate_ids == ("B", "C")
    assert selector.active_candidate_id == "A"
    assert selector.bench_ids == ("B", "C")


def test_reconstruct_rejects_active_candidate_in_bench() -> None:
    selector = SMCROMSelector(bench_capacity=3)
    with pytest.raises(ValueError, match="active candidate cannot be part"):
        selector.reconstruct(("A", "B"), "A", "restart/session-1")


def test_reconstruct_rejects_unbounded_state() -> None:
    selector = SMCROMSelector(bench_capacity=2)
    with pytest.raises(ValueError, match="exceeds capacity"):
        selector.reconstruct(("A", "B", "C"), None, "restart/session-2")


def test_candidate_record_is_immutable_and_model_free() -> None:
    item = candidate("A")
    with pytest.raises(FrozenInstanceError):
        item.candidate_id = "B"  # type: ignore[misc]
    assert not hasattr(item, "model")
    assert not hasattr(item, "peer_model")


def test_default_bench_capacity_is_constitutional_limit() -> None:
    assert BENCH_CAPACITY == 10


def test_invalid_model_cannot_be_activated_by_replace() -> None:
    selector = SMCROMSelector()
    selector.select(candidate("A"))
    decision = selector.replace(candidate("B", contract=False))
    assert decision.resulting_state is CandidateState.INVALID
    assert selector.active_candidate_id == "A"
