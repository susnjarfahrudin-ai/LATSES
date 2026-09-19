import pytest

from lat_ces.rci_ad.security_event import SecurityEvent
from lat_ces.rci_ad.security_event_ledger import SecurityEventLedger


def make_event(sequence=1, reason="observed"):
    return SecurityEvent(
        event_type="FLOW_OBSERVED",
        source_id="flowguard",
        reason=reason,
        timestamp=1000.0 + sequence,
        sequence=sequence,
    )


def test_security_event_is_immutable():
    event = make_event()
    with pytest.raises(Exception):
        event.reason = "changed"


@pytest.mark.parametrize(
    "field,value",
    [
        ("event_type", ""),
        ("source_id", ""),
        ("reason", ""),
        ("timestamp", float("nan")),
        ("sequence", -1),
        ("sequence", True),
    ],
)
def test_invalid_security_event_fields_are_rejected(field, value):
    kwargs = {
        "event_type": "FLOW_OBSERVED",
        "source_id": "flowguard",
        "reason": "observed",
        "timestamp": 1000.0,
        "sequence": 1,
    }
    kwargs[field] = value
    with pytest.raises(ValueError):
        SecurityEvent(**kwargs)


def test_ledger_is_append_only_and_preserves_repeated_events():
    ledger = SecurityEventLedger()
    first = make_event(sequence=1, reason="first")
    second = make_event(sequence=2, reason="second")
    third = make_event(sequence=3, reason="third")

    ledger.append(first)
    ledger.append(second)
    ledger.append(third)

    assert len(ledger) == 3
    assert ledger.events() == (first, second, third)
    assert [event.reason for event in ledger.events()] == ["first", "second", "third"]


def test_same_source_and_event_type_are_not_overwritten():
    ledger = SecurityEventLedger()
    first = make_event(sequence=1, reason="first")
    second = make_event(sequence=2, reason="second")
    ledger.append(first)
    ledger.append(second)
    assert ledger.events() == (first, second)


def test_ledger_snapshot_is_read_only():
    ledger = SecurityEventLedger()
    ledger.append(make_event())
    snapshot = ledger.events()
    assert isinstance(snapshot, tuple)
    with pytest.raises(AttributeError):
        snapshot.append(make_event(sequence=2))


def test_ledger_has_no_defense_enforcement_side_effect():
    ledger = SecurityEventLedger()
    event = SecurityEvent(
        event_type="ISOLATION_REQUESTED",
        source_id="flowguard",
        reason="record only",
        timestamp=1000.0,
        sequence=1,
    )
    ledger.append(event)
    assert ledger.events() == (event,)
