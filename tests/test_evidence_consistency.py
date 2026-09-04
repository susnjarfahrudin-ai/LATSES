from dataclasses import FrozenInstanceError

from lat_ces.structural.decision_record_store import DecisionRecord, DecisionRecordStore
from lat_ces.structural.evidence_consistency import EvidenceConsistencyChecker, EvidenceConsistencyResult


def record(decision_id="d1", model_version="model-v1", selector_version="selector-v1"):
    return DecisionRecord(
        decision_id=decision_id,
        timestamp="2026-09-04T00:00:00Z",
        session_id="session-1",
        model_id="model-1",
        model_version=model_version,
        previous_state=None,
        resulting_state="ACTIVE",
        reason="verified",
        evidence="evidence",
        applicability_passed=True,
        contract_passed=True,
        supersedes_decision_id=None,
        selector_version=selector_version,
    )


def store_with(*records):
    store = DecisionRecordStore()
    for item in records:
        store.append(item)
    return store


def test_consistent_preserved_evidence_is_accepted():
    store = store_with(record("d1"), record("d2"))

    result = EvidenceConsistencyChecker().check(
        store,
        ("d1", "d2"),
        model_version="model-v1",
        selector_version="selector-v1",
    )

    assert isinstance(result, EvidenceConsistencyResult)
    assert result.consistent is True
    assert result.reason == "consistent"
    assert result.model_versions == ("model-v1", "model-v1")


def test_missing_decision_id_is_rejected():
    store = store_with(record("d1"))

    result = EvidenceConsistencyChecker().check(
        store,
        ("d1", "d2"),
        model_version="model-v1",
        selector_version="selector-v1",
    )

    assert result.consistent is False
    assert result.reason == "decision_id not found: d2"


def test_duplicate_decision_id_is_rejected_without_store_mutation():
    store = store_with(record("d1"))
    before = store.records

    result = EvidenceConsistencyChecker().check(
        store,
        ("d1", "d1"),
        model_version="model-v1",
        selector_version="selector-v1",
    )

    assert result.consistent is False
    assert result.reason == "decision_ids must be unique"
    assert store.records == before


def test_selector_version_mismatch_is_rejected():
    store = store_with(record("d1", selector_version="selector-v2"))

    result = EvidenceConsistencyChecker().check(
        store,
        ("d1",),
        model_version="model-v1",
        selector_version="selector-v1",
    )

    assert result.consistent is False
    assert result.reason == "selector_version mismatch"


def test_model_version_mismatch_is_rejected():
    store = store_with(record("d1", model_version="model-v2"))

    result = EvidenceConsistencyChecker().check(
        store,
        ("d1",),
        model_version="model-v1",
        selector_version="selector-v1",
    )

    assert result.consistent is False
    assert result.reason == "model_version mismatch"


def test_consistency_result_is_immutable():
    result = EvidenceConsistencyChecker().check(
        store_with(record("d1")),
        ("d1",),
        model_version="model-v1",
        selector_version="selector-v1",
    )

    try:
        result.reason = "changed"
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("consistency result must be immutable")


def test_checker_has_no_selector_or_model_implementation_state():
    checker = EvidenceConsistencyChecker()
    assert not hasattr(checker, "selector")
    assert not hasattr(checker, "model")
