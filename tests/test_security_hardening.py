import json
import os
from dataclasses import FrozenInstanceError

import pytest

from lat_ces.security.atomic_persistence import atomic_write_bytes
from lat_ces.security.keyring import KeyRing, hkdf_sha256
from lat_ces.security.rate_limit import TokenBucket, TokenBucketRateLimiter
from lat_ces.security.secure_ipc import ReplayGuard, SecurityError, SignedIPCChannel
from lat_ces.security.secure_memory import secure_zero
from lat_ces.security.threat_score import ThreatScoreEngine, ThreatScorePolicy
from lat_ces.security.process_security import current_process_identity, is_process_alive


class MemoryStore:
    def __init__(self) -> None:
        self.values: dict[tuple[str, str], str] = {}

    def get_password(self, service: str, account: str) -> str | None:
        return self.values.get((service, account))

    def set_password(self, service: str, account: str, password: str) -> None:
        self.values[(service, account)] = password


def test_secure_zero_clears_mutable_buffer() -> None:
    value = bytearray(b"secret")
    secure_zero(value)
    assert value == b"\0" * 6


def test_atomic_write_replaces_target(tmp_path) -> None:
    target = tmp_path / "state.enc"
    target.write_bytes(b"old")
    atomic_write_bytes(target, b"new")
    assert target.read_bytes() == b"new"
    assert not list(tmp_path.glob(".*.tmp-*"))


def test_keyring_versions_and_hkdf_are_stable() -> None:
    store = MemoryStore()
    ring = KeyRing(store=store)
    assert ring.initialize() == 1
    assert ring.current_version() == 1
    with ring.borrow_derived_key(purpose=b"ipc") as first:
        first_value = bytes(first)
    assert first == b"\0" * len(first)
    version = ring.rotate()
    assert version == 2
    with ring.borrow_derived_key(purpose=b"ipc", version=1) as old:
        old_value = bytes(old)
    with ring.borrow_derived_key(purpose=b"ipc", version=2) as new:
        new_value = bytes(new)
    assert old_value == first_value
    assert new_value != old_value
    assert hkdf_sha256(b"input", info=b"test", length=16) != hkdf_sha256(b"input", info=b"other", length=16)


def test_keyring_never_overwrites_existing_version() -> None:
    store = MemoryStore()
    ring = KeyRing(store=store)
    ring.initialize()
    original = store.values[("LAT-CES", "root/v1")]
    assert ring.initialize() == 1
    assert store.values[("LAT-CES", "root/v1")] == original


def _channel() -> SignedIPCChannel:
    return SignedIPCChannel(b"shared-secret", replay_guard=ReplayGuard(ttl_seconds=30))


def test_signed_ipc_accepts_valid_message_and_rejects_replay() -> None:
    channel = _channel()
    packet = channel.pack({"heartbeat": True}, sender_id="consul-a")
    assert channel.unpack(packet) == {"heartbeat": True}
    with pytest.raises(SecurityError, match="replay"):
        channel.unpack(packet)


def test_signed_ipc_rejects_tampering() -> None:
    channel = _channel()
    packet = channel.pack({"value": 1}, sender_id="consul-a")
    decoded = json.loads(packet.decode())
    decoded["envelope"]["payload"]["value"] = 2
    with pytest.raises(SecurityError, match="authentication"):
        channel.unpack(json.dumps(decoded, separators=(",", ":")).encode())


def test_signed_ipc_rejects_excessive_future_skew() -> None:
    channel = SignedIPCChannel(b"shared-secret", max_future_skew_seconds=5)
    packet = channel.pack({"value": 1}, sender_id="consul-a")
    decoded = json.loads(packet.decode())
    decoded["envelope"]["timestamp"] = decoded["envelope"]["timestamp"] + 10
    envelope = decoded["envelope"]
    import hashlib
    import hmac
    canonical = json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    decoded["mac"] = hmac.new(b"shared-secret", canonical, hashlib.sha256).hexdigest()
    with pytest.raises(SecurityError, match="timestamp"):
        channel.unpack(json.dumps(decoded, separators=(",", ":")).encode())


def test_rate_limiter_is_deterministic_and_refills() -> None:
    limiter = TokenBucketRateLimiter(capacity=3, refill_per_second=1, idle_ttl_seconds=30)
    assert limiter.allow("10.0.0.1", now=100.0)
    assert limiter.allow("10.0.0.1", now=100.0)
    assert limiter.allow("10.0.0.1", now=100.0)
    assert not limiter.allow("10.0.0.1", now=100.0)
    assert limiter.allow("10.0.0.1", now=101.0)
    assert limiter.allow("10.0.0.2", now=101.0)


def test_token_bucket_rejects_invalid_cost_and_policy() -> None:
    with pytest.raises(ValueError):
        TokenBucket(capacity=0, refill_per_second=1)
    bucket = TokenBucket(capacity=1, refill_per_second=1, updated_at=0.0)
    with pytest.raises(ValueError):
        bucket.allow(now=0.0, cost=0)


def test_threat_score_decays_and_whitelist_cannot_be_blocked() -> None:
    policy = ThreatScorePolicy(decay_window_seconds=10, block_threshold=5, whitelist=("127.0.0.0/8",))
    engine = ThreatScoreEngine(policy)
    assert engine.record("10.0.0.5", 8, now=100.0) == 8
    assert engine.should_block("10.0.0.5", now=100.0)
    assert engine.score("10.0.0.5", now=110.0) < 8
    assert engine.record("127.0.0.1", 100, now=100.0) == 0
    assert not engine.should_block("127.0.0.1", now=100.0)


def test_process_identity_uses_pid_and_kernel_start_token() -> None:
    identity = current_process_identity()
    assert identity.pid == os.getpid()
    assert identity.process_uuid
    assert identity.created_at_utc
    assert identity.kernel_start_token
    assert is_process_alive(identity.pid, identity.fingerprint)
    assert not is_process_alive(identity.pid, identity.fingerprint + "-changed")


def test_process_identity_is_immutable() -> None:
    identity = current_process_identity()
    with pytest.raises(FrozenInstanceError):
        identity.pid = -1  # type: ignore[misc]
