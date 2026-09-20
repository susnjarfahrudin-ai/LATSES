import json

import pytest

from lat_ces.security.atomic_persistence import atomic_write_bytes
from lat_ces.security.cyber_fortress import CyberFortress
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


def test_fortress_routes_authenticated_request_through_boundary() -> None:
    channel = SignedIPCChannel(b"shared-secret")
    fortress = CyberFortress(channel)
    packet = channel.pack({"operation": "read"}, sender_id="trusted")

    assert fortress.admit("10.0.0.8", now=100.0).allowed
    assert fortress.receive("10.0.0.8", packet, now=100.0) == {"operation": "read"}


def test_fortress_rejects_unauthenticated_ipc_and_records_threat() -> None:
    channel = SignedIPCChannel(b"shared-secret")
    fortress = CyberFortress(channel)
    packet = channel.pack({"operation": "read"}, sender_id="trusted")
    forged = json.loads(packet.decode("utf-8"))
    forged["mac"] = "0" * 64
    forged_packet = json.dumps(forged, separators=(",", ":")).encode("utf-8")

    with pytest.raises(SecurityError):
        fortress.receive("10.0.0.9", forged_packet, now=100.0)
    assert fortress.threat.score("10.0.0.9", now=100.0) >= 25.0


def test_fortress_rate_limit_is_before_ipc() -> None:
    channel = SignedIPCChannel(b"shared-secret")
    limiter = TokenBucketRateLimiter(capacity=1.0, refill_per_second=1.0)
    fortress = CyberFortress(channel, rate_limiter=limiter)
    packet = channel.pack({"operation": "read"}, sender_id="trusted")

    assert fortress.receive("10.0.0.10", packet, now=100.0) == {"operation": "read"}
    with pytest.raises(SecurityError, match="rate-limited"):
        fortress.receive("10.0.0.10", packet, now=100.0)


def test_threat_policy_blocks_before_ipc() -> None:
    channel = SignedIPCChannel(b"shared-secret")
    engine = ThreatScoreEngine(ThreatScorePolicy(block_threshold=20.0))
    fortress = CyberFortress(channel, threat_engine=engine)
    engine.record("10.0.0.11", 20.0, now=100.0)
    packet = channel.pack({"operation": "read"}, sender_id="trusted")

    with pytest.raises(SecurityError, match="threat-blocked"):
        fortress.receive("10.0.0.11", packet, now=100.0)


def test_replay_guard_capacity_attack_is_caught_by_unified_suite() -> None:
    guard = ReplayGuard(ttl_seconds=120, max_entries=2)
    assert guard.check_and_add("victim", now=100.0)
    assert guard.check_and_add("a", now=100.0)
    assert guard.check_and_add("b", now=100.0)
    # Security invariant: bounded-cache pressure must never make a previously
    # accepted nonce valid again while it is still inside its replay TTL.
    assert not guard.check_and_add("victim", now=100.0)


def test_ipc_rejects_non_finite_timestamp_at_boundary() -> None:
    channel = SignedIPCChannel(b"shared-secret")
    packet = channel.pack({"attack": "nan"}, sender_id="probe")
    decoded = json.loads(packet.decode("utf-8"))
    decoded["envelope"]["timestamp"] = float("nan")
    with pytest.raises(SecurityError):
        channel.unpack(json.dumps(decoded, separators=(",", ":")).encode("utf-8"))


def test_secure_memory_clears_mutable_secret() -> None:
    secret = bytearray(b"sensitive-secret")
    secure_zero(secret)
    assert secret == bytearray(len(secret))


def test_atomic_persistence_replaces_target(tmp_path) -> None:
    target = tmp_path / "state.bin"
    atomic_write_bytes(target, b"canonical-state")
    assert target.read_bytes() == b"canonical-state"


def test_keyring_initialization_and_rotation_keep_versioned_keys() -> None:
    store = MemorySecretStore()
    ring = KeyRing(service="LAT-CES-test", store=store)
    assert ring.initialize() == 1
    assert ring.current_version() == 1
    assert ring.rotate() == 2
    with ring.borrow_root_key() as key:
        assert len(key) == 32
    with ring.borrow_derived_key(purpose=b"ipc") as key:
        assert len(key) == 32


def test_process_identity_has_stable_pid_and_start_fingerprint() -> None:
    identity = current_process_identity()
    assert identity.pid > 0
    assert identity.kernel_start_token
    assert identity.fingerprint.startswith(f"{identity.pid}:")
