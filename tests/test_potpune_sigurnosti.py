import json

import pytest

from lat_ces.security.adaptive_defense import AdaptiveDefense
from lat_ces.security.atomic_persistence import atomic_write_bytes
from lat_ces.security.cyber_fortress import CyberFortress
from lat_ces.security.defense_history import DefenseHistory
from lat_ces.security.keyring import KeyRing
from lat_ces.security.process_security import current_process_identity
from lat_ces.security.rate_limit import TokenBucketRateLimiter
from lat_ces.security.secure_ipc import ReplayGuard, SecurityError, SignedIPCChannel
from lat_ces.security.secure_memory import secure_zero
from lat_ces.security.threat_score import ThreatScoreEngine, ThreatScorePolicy


class MemorySecretStore:
    def __init__(self):
        self.values = {}

    def get_password(self, service, account):
        return self.values.get((service, account))

    def set_password(self, service, account, password):
        self.values[(service, account)] = password


def test_fortress_routes_authenticated_request_through_boundary():
    channel = SignedIPCChannel(b"shared-secret")
    fortress = CyberFortress(channel)
    packet = channel.pack({"operation": "read"}, sender_id="trusted")
    assert fortress.admit("10.0.0.8", now=100.0).allowed
    assert fortress.receive("10.0.0.8", packet, now=100.0) == {"operation": "read"}


def test_fortress_rejects_unauthenticated_ipc_and_records_threat():
    channel = SignedIPCChannel(b"shared-secret")
    fortress = CyberFortress(channel)
    packet = channel.pack({"operation": "read"}, sender_id="trusted")
    forged = json.loads(packet.decode("utf-8"))
    forged["mac"] = "0" * 64
    forged_packet = json.dumps(forged, separators=(",", ":")).encode("utf-8")
    with pytest.raises(SecurityError):
        fortress.receive("10.0.0.9", forged_packet, now=100.0)
    assert fortress.threat.score("10.0.0.9", now=100.0) >= 25.0
    assert fortress.adaptive_defense.records()[0].attack_class == "ipc-rejection"


def test_fortress_rate_limit_is_before_ipc():
    channel = SignedIPCChannel(b"shared-secret")
    limiter = TokenBucketRateLimiter(capacity=1.0, refill_per_second=1.0)
    fortress = CyberFortress(channel, rate_limiter=limiter)
    packet = channel.pack({"operation": "read"}, sender_id="trusted")
    assert fortress.receive("10.0.0.10", packet, now=100.0) == {"operation": "read"}
    with pytest.raises(SecurityError, match="rate-limited"):
        fortress.receive("10.0.0.10", packet, now=100.0)


def test_threat_policy_blocks_before_ipc():
    channel = SignedIPCChannel(b"shared-secret")
    engine = ThreatScoreEngine(ThreatScorePolicy(block_threshold=20.0))
    fortress = CyberFortress(channel, threat_engine=engine)
    engine.record("10.0.0.11", 20.0, now=100.0)
    packet = channel.pack({"operation": "read"}, sender_id="trusted")
    with pytest.raises(SecurityError, match="threat-blocked"):
        fortress.receive("10.0.0.11", packet, now=100.0)


def test_replay_guard_capacity_attack_is_caught_by_unified_suite():
    guard = ReplayGuard(ttl_seconds=120, max_entries=2)
    assert guard.check_and_add("victim", now=100.0)
    assert guard.check_and_add("a", now=100.0)
    assert guard.check_and_add("b", now=100.0)
    assert not guard.check_and_add("victim", now=100.0)


def test_ipc_rejects_non_finite_timestamp_at_boundary():
    channel = SignedIPCChannel(b"shared-secret")
    packet = channel.pack({"attack": "nan"}, sender_id="probe")
    decoded = json.loads(packet.decode("utf-8"))
    decoded["envelope"]["timestamp"] = float("nan")
    with pytest.raises(SecurityError):
        channel.unpack(json.dumps(decoded, separators=(",", ":")).encode("utf-8"))


def test_secure_memory_clears_mutable_secret():
    secret = bytearray(b"sensitive-secret")
    secure_zero(secret)
    assert secret == bytearray(len(secret))


def test_atomic_persistence_replaces_target(tmp_path):
    target = tmp_path / "state.bin"
    atomic_write_bytes(target, b"canonical-state")
    assert target.read_bytes() == b"canonical-state"


def test_keyring_initialization_and_rotation_keep_versioned_keys():
    store = MemorySecretStore()
    ring = KeyRing(service="LAT-CES-test", store=store)
    assert ring.initialize() == 1
    assert ring.current_version() == 1
    assert ring.rotate() == 2
    with ring.borrow_root_key() as key:
        assert len(key) == 32
    with ring.borrow_derived_key(purpose=b"ipc") as key:
        assert len(key) == 32


def test_process_identity_has_stable_pid_and_start_fingerprint():
    identity = current_process_identity()
    assert identity.pid > 0
    assert identity.kernel_start_token
    assert identity.fingerprint.startswith(f"{identity.pid}:")


def test_adaptive_defense_a_failure_quarantine_b_then_verified_return_to_a():
    a = AdaptiveDefense()
    b = AdaptiveDefense()
    failure = a.observe_failure("ipc:malformed IPC nonce", "ipc-rejection", "zero-width-space", source="A")
    b.quarantine(failure)
    assert b.is_quarantined(failure.invariant_id)
    verified = b.promote(failure, verification_sha="verification-sha-001")
    assert verified.verified
    assert verified.digest
    a.import_verified(verified)
    assert a.is_quarantined(verified.invariant_id)
    assert a.export_verified() == (verified,)


def test_unverified_adaptive_defense_cannot_be_promoted_or_imported():
    a = AdaptiveDefense()
    b = AdaptiveDefense()
    record = a.observe_failure("ipc:test", "ipc-rejection", "proof", source="A")
    with pytest.raises(ValueError):
        b.import_verified(record)
    with pytest.raises(ValueError):
        b.promote(record, verification_sha="")


def test_defense_history_reads_evidence_but_exposes_only_verified_lessons(tmp_path):
    path = tmp_path / "history.jsonl"
    records = [
        {"record_id": "observed-1", "status": "contained", "attack_class": "probe", "invariant": "fixed baseline", "dimensions": ["frequency", "volume", "concurrency", "novelty"], "baseline": {"frequency": 100, "volume": 100, "concurrency": 100, "novelty": 100}, "observation": {"deviation": 0.19}, "response": {"action": "throttle"}, "verification_sha": None},
        {"record_id": "verified-1", "status": "learned", "attack_class": "flow-edge", "invariant": "20% admission stop", "dimensions": ["frequency"], "baseline": {"frequency": 100, "volume": 100, "concurrency": 100, "novelty": 100}, "observation": {"deviation": 0.20, "duration_seconds": 1.0}, "response": {"action": "admission-stop"}, "verification_sha": "verification-sha-002"},
    ]
    path.write_text("\n".join(json.dumps(item, sort_keys=True) for item in records) + "\n", encoding="utf-8")
    history = DefenseHistory(path)
    assert len(history.records()) == 2
    assert [item.record_id for item in history.verified_lessons()] == ["verified-1"]
    with pytest.raises(TypeError):
        history.records()[0].baseline["frequency"] = 200
    assert not hasattr(history, "append")
    assert not hasattr(history, "write")


def test_defense_history_fails_closed_on_unverified_record_marked_learned(tmp_path):
    path = tmp_path / "history.jsonl"
    record = {"record_id": "bad-1", "status": "learned", "attack_class": "probe", "invariant": "x", "dimensions": ["frequency"], "baseline": {"frequency": 100, "volume": 100, "concurrency": 100, "novelty": 100}, "observation": {}, "response": {}, "verification_sha": None}
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="verification_sha"):
        DefenseHistory(path)
