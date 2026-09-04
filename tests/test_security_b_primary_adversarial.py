import hashlib
import hmac
import json
import math
import time

import pytest

from lat_ces.security.adaptive_defense import AdaptiveDefense
from lat_ces.security.cyber_fortress import CyberFortress
from lat_ces.security.flow_guard import FlowGuard
from lat_ces.security.secure_ipc import SecurityError, SignedIPCChannel


def _resign(packet: bytes, mutate) -> bytes:
    decoded = json.loads(packet.decode("utf-8"))
    mutate(decoded["envelope"])
    canonical = json.dumps(
        decoded["envelope"], sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    decoded["mac"] = hmac.new(b"shared-secret", canonical, hashlib.sha256).hexdigest()
    return json.dumps(decoded, separators=(",", ":")).encode("utf-8")


def _attacks(channel: SignedIPCChannel) -> list[bytes]:
    base = channel.pack({"attack": "b-primary"}, sender_id="attacker-probe")
    return [
        _resign(base, lambda e: e.__setitem__("timestamp", float("nan"))),
        _resign(base, lambda e: e.__setitem__("timestamp", float("inf"))),
        _resign(base, lambda e: e.__setitem__("v", True)),
        _resign(base, lambda e: e.__setitem__("nonce", None)),
        _resign(base, lambda e: e.__setitem__("sender_id", None)),
        _resign(base, lambda e: e.__setitem__("payload", [])),
        _resign(base, lambda e: e.__setitem__("sender_id", "   \t\n")),
        _resign(base, lambda e: e.__setitem__("nonce", "   \t\n")),
        _resign(base, lambda e: e.__setitem__("sender_id", True)),
        _resign(base, lambda e: e.__setitem__("nonce", "\u200b")),
        base.decode("utf-8"),
    ]


def test_b_primary_survives_five_minute_four_dimension_adversarial_burst() -> None:
    """Swap roles: B is primary under attack; A is standby and receives no trust shortcut."""
    b = CyberFortress(SignedIPCChannel(b"shared-secret"), adaptive_defense=AdaptiveDefense())
    a = CyberFortress(SignedIPCChannel(b"shared-secret"), adaptive_defense=AdaptiveDefense())
    guard_b = FlowGuard({d: 100.0 for d in ("frequency", "volume", "concurrency", "novelty")})
    guard_a = FlowGuard({d: 100.0 for d in ("frequency", "volume", "concurrency", "novelty")})

    start = time.monotonic()
    duration = 300.0
    phase = 0
    attack_packets = _attacks(b.ipc)

    while time.monotonic() - start < duration:
        elapsed = time.monotonic() - start
        t = elapsed / duration
        # Quiet, spike, paired, reverse zig-zag, near-limit and recovery phases.
        wave = 1.0 + (0.02 if phase % 2 == 0 else -0.02)
        if 0.12 < t < 0.20:
            wave = 1.20
        elif 0.20 <= t < 0.28:
            wave = 0.80
        elif 0.28 <= t < 0.45:
            wave = 1.12 if phase % 3 else 0.88
        elif 0.45 <= t < 0.65:
            wave = 1.18 if phase % 4 in (0, 1) else 0.82
        elif 0.65 <= t < 0.82:
            wave = 1.195 if phase % 2 == 0 else 0.805
        elif 0.82 <= t:
            wave = 1.02 if phase % 2 == 0 else 0.98

        values = {
            "frequency": 100.0 * wave,
            "volume": 100.0 * (1.0 + ((wave - 1.0) * 0.75)),
            "concurrency": 100.0 * (1.0 + ((wave - 1.0) * 1.10)),
            "novelty": 100.0 * (1.0 - ((wave - 1.0) * 0.90)),
        }
        decision_b = guard_b.evaluate(values)
        decision_a = guard_a.evaluate(values)
        assert decision_b.allowed == decision_a.allowed
        assert math.isclose(decision_b.throttle, decision_a.throttle, rel_tol=1e-12, abs_tol=1e-12)
        assert decision_b.max_deviation == decision_a.max_deviation

        packet = attack_packets[phase % len(attack_packets)]
        try:
            b.receive("203.0.113.42", packet, now=time.time())
        except SecurityError:
            pass

        phase += 1
        time.sleep(0.05)

    assert phase > 1000
    b_records = b.adaptive_defense.records()
    assert b_records, "B did not record any primary-side security failures"
    assert all(record.source == "A" for record in b_records)
    assert not a.adaptive_defense.records(), "standby A learned from unverified B observations"
    assert guard_b.baseline == guard_a.baseline == {
        "frequency": 100.0,
        "volume": 100.0,
        "concurrency": 100.0,
        "novelty": 100.0,
    }
