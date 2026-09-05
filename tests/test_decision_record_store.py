import pytest

from lat_ces.structural.decision_record_store import DecisionRecord, DecisionRecordStore


def record(decision_id: str, *, supersedes: str | None = None) -> DecisionRecord:
    return DecisionRecord(
        decision_id=decision_id,
        timestamp="2026-09-04T00:00:00Z",
        session_id="session-1",
        model_id="candidate-1",
        model_version="1.0",
        previous_state="BENCHED",
        resulting_state="ACTIVE",
        reason="eligible takeover candidate",
        evidence="registry/candidate-1",
        applicability_passed=True,
        contract_passed=True,
        supersedes_decision_id=supersedes,
        selector_version="smc-rom-v1",
    )


def test_store_preserves_append_order_and_history() -> None:
    store = DecisionRecordStore()
    first = store.append(record("decision-1"))
    second = store.append(record("decision-2", supersedes="decision-1"))

    assert store.records == (first, second)
    assert store.get("decision-1") is first
    assert store.get("decision-2") is second


def test_duplicate_decision_id_cannot_rewrite_history() -> None:
    store = DecisionRecordStore()
    store.append(record("decision-1"))

    with pytest.raises(ValueError, match="decision_id already exists"):
        store.append(record("decision-1"))

    assert len(store.records) == 1


def test_record_is_immutable() -> None:
    record_value = record("decision-1")

    with pytest.raises(AttributeError):
        record_value.resulting_state = "RETIRED"  # type: ignore[misc]


def test_record_contains_required_neutral_provenance_fields() -> None:
    value = record("decision-1")

    assert value.decision_id
    assert value.timestamp
    assert value.session_id
    assert value.model_id
    assert value.model_version
    assert value.previous_state == "BENCHED"
    assert value.resulting_state == "ACTIVE"
    assert value.reason
    assert value.evidence
    assert value.applicability_passed is True
    assert value.contract_passed is True
    assert value.supersedes_decision_id is None
    assert value.selector_version


def test_store_does_not_expose_model_implementation_or_selector_state() -> None:
    store = DecisionRecordStore()
    store.append(record("decision-1"))

    assert not hasattr(store, "model")
    assert not hasattr(store, "selector")
    assert not hasattr(store.records[0], "peer_model")
