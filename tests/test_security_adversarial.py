import hashlib
import hmac
import json

import pytest

from lat_ces.building.model_recovery_record import ModelRecoveryRecord
from lat_ces.security.secure_ipc import ReplayGuard, SecurityError, SignedIPCChannel


def _resign(packet: bytes, mutate) -> bytes:
    decoded = json.loads(packet.decode("utf-8"))
    mutate(decoded["envelope"])
    canonical = json.dumps(
        decoded["envelope"], sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    decoded["mac"] = hmac.new(b"shared-secret", canonical, hashlib.sha256).hexdigest()
    return json.dumps(decoded, separators=(",", ":")).encode("utf-8")


def test_ipc_rejects_nan_timestamp_even_when_mac_is_valid() -> None:
    channel = SignedIPCChannel(b"shared-secret")
    packet = channel.pack({"attack": "nan"}, sender_id="attacker-probe")
    forged = _resign(packet, lambda envelope: envelope.__setitem__("timestamp", float("nan")))
    with pytest.raises(SecurityError):
        channel.unpack(forged)


def test_ipc_rejects_infinite_timestamp_even_when_mac_is_valid() -> None:
    channel = SignedIPCChannel(b"shared-secret")
    packet = channel.pack({"attack": "inf"}, sender_id="attacker-probe")
    forged = _resign(packet, lambda envelope: envelope.__setitem__("timestamp", float("inf")))
    with pytest.raises(SecurityError):
        channel.unpack(forged)


def test_replay_guard_cannot_be_primed_into_accepting_an_old_nonce() -> None:
    guard = ReplayGuard(ttl_seconds=120, max_entries=2)
    assert guard.check_and_add("victim", now=100.0)
    assert guard.check_and_add("a", now=100.0)
    assert guard.check_and_add("b", now=100.0)
    assert not guard.check_and_add("victim", now=100.0)


def test_ipc_rejects_malformed_envelope_types() -> None:
    channel = SignedIPCChannel(b"shared-secret")
    packet = channel.pack({"value": 1}, sender_id="probe")
    decoded = json.loads(packet.decode("utf-8"))
    decoded["envelope"] = []
    malformed = json.dumps(decoded, separators=(",", ":")).encode("utf-8")
    with pytest.raises(SecurityError):
        channel.unpack(malformed)


def test_recovery_record_rejects_each_authoritative_metadata_mutation() -> None:
    record = ModelRecoveryRecord.create(
        record_id="REC-ATTACK",
        model_id="MODEL-A",
        revision=7,
        parent_revision=6,
        lifecycle_status="VALID",
        selector_role="PRIMARY",
        payload={"geometry": {"wall": 1}},
    )
    baseline = record.to_dict()
    for field, value in {
        "record_id": "REC-FORGED",
        "model_id": "MODEL-FORGED",
        "revision": 8,
        "parent_revision": 5,
        "created_at": "2099-01-01T00:00:00+00:00",
        "lifecycle_status": "REVOKED",
        "selector_role": "FALLBACK",
        "payload": {"geometry": {"wall": 999}},
    }.items():
        tampered = dict(baseline)
        tampered[field] = value
        with pytest.raises(ValueError):
            ModelRecoveryRecord.from_dict(tampered)


def test_recovery_record_rejects_nested_payload_mutation() -> None:
    record = ModelRecoveryRecord.create(
        record_id="REC-NESTED",
        model_id="MODEL-A",
        revision=1,
        payload={"geometry": {"wall": {"thickness": 0.20}}},
    )
    tampered = record.to_dict()
    tampered["payload"]["geometry"]["wall"]["thickness"] = 99.0
    with pytest.raises(ValueError):
        ModelRecoveryRecord.from_dict(tampered)
