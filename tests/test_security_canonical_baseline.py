from __future__ import annotations

import pytest

from lat_ces.security import AdaptiveDefense, CyberFortress, DefenseRecord
from lat_ces.security.secure_ipc import SecurityError, SignedIPCChannel


def test_adaptive_defense_requires_verified_import() -> None:
    active = AdaptiveDefense()
    standby = AdaptiveDefense()
    record = active.observe_failure(
        "ipc:test",
        "ipc-rejection",
        "malformed packet",
        source="A",
    )

    with pytest.raises(ValueError):
        standby.import_verified(record)

    verified = standby.promote(record, verification_sha="verification-sha")
    active.import_verified(verified)
    assert active.export_verified() == (verified,)
    assert standby.is_quarantined("ipc:test")


def test_cyber_fortress_records_ipc_failure_as_defense_evidence() -> None:
    fortress = CyberFortress(SignedIPCChannel(b"shared-secret"))
    with pytest.raises(SecurityError):
        fortress.receive("203.0.113.10", b"not-json", now=1_000.0)

    records = fortress.adaptive_defense.records()
    assert records
    assert records[0].source == "A"
    assert records[0].attack_class == "ipc-rejection"


def test_verified_defense_handoff_does_not_copy_unverified_records() -> None:
    active = CyberFortress(SignedIPCChannel(b"shared-secret"))
    standby = CyberFortress(SignedIPCChannel(b"shared-secret"))

    unverified = active.adaptive_defense.observe_failure(
        "ipc:unverified",
        "ipc-rejection",
        "evidence",
        source="A",
    )
    assert unverified.verified is False
    assert active.handoff_verified_defense(standby) == 0
    assert not standby.adaptive_defense.records()

    verified = active.adaptive_defense.promote(unverified, verification_sha="sha-001")
    assert active.handoff_verified_defense(standby) == 1
    assert standby.adaptive_defense.export_verified() == (verified,)


def test_defense_record_is_immutable_and_digest_is_stable() -> None:
    record = DefenseRecord("id", "attack", "evidence", "A")
    with pytest.raises(AttributeError):
        record.source = "B"  # type: ignore[misc]
    assert record.digest == record.digest
