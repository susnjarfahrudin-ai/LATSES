"""Controlled adversarial audit against exact main baseline 4871bfc.
Test-only: no production security code is changed.
"""
from __future__ import annotations
import pytest
from lat_ces.security.cyber_fortress import CyberFortress
from lat_ces.security.flow_guard import FlowGuard
from lat_ces.security.secure_ipc import SecurityError, SignedIPCChannel
from lat_ces.security.rate_limit import TokenBucketRateLimiter

SECRET = b"controlled-audit-secret"
ATTACKER = "198.51.100.77"

def test_attack_01_bad_mac_is_rejected_and_recorded():
    channel = SignedIPCChannel(SECRET)
    fortress = CyberFortress(channel)
    packet = bytearray(channel.pack({"op": "probe"}, sender_id=ATTACKER))
    packet[-2] = ord("0") if packet[-2] != ord("0") else ord("1")
    with pytest.raises(SecurityError):
        fortress.receive(ATTACKER, bytes(packet))
    records = fortress.adaptive_defense.records()
    assert len(records) == 1
    assert records[0].attack_class == "ipc-rejection"
    assert fortress.threat.score(ATTACKER) == pytest.approx(25.0, abs=1e-3)

def test_attack_02_replay_is_rejected_after_first_acceptance():
    channel = SignedIPCChannel(SECRET)
    fortress = CyberFortress(channel)
    packet = channel.pack({"op": "replay-probe"}, sender_id=ATTACKER)
    assert fortress.receive(ATTACKER, packet)["op"] == "replay-probe"
    with pytest.raises(SecurityError, match="replay"):
        fortress.receive(ATTACKER, packet)

def test_attack_03_rate_pressure_eventually_blocks_without_flowguard():
    limiter = TokenBucketRateLimiter(capacity=2.0, refill_per_second=1.0)
    fortress = CyberFortress(SignedIPCChannel(SECRET), rate_limiter=limiter)
    packet = fortress.ipc.pack({"op": "pressure"}, sender_id=ATTACKER)
    assert fortress.receive(ATTACKER, packet)["op"] == "pressure"
    packet2 = fortress.ipc.pack({"op": "pressure-2"}, sender_id=ATTACKER)
    assert fortress.receive(ATTACKER, packet2)["op"] == "pressure-2"
    with pytest.raises(SecurityError, match="rate-limited"):
        fortress.receive(ATTACKER, fortress.ipc.pack({"op": "pressure-3"}, sender_id=ATTACKER))
    assert fortress.threat.score(ATTACKER) == pytest.approx(10.0, abs=1e-3)

def test_attack_04_flowguard_hard_stop_is_real_but_not_called_by_fortress():
    guard = FlowGuard({name: 100.0 for name in ("frequency", "volume", "concurrency", "novelty")})
    decision = guard.evaluate({"frequency": 120.0, "volume": 100.0, "concurrency": 100.0, "novelty": 100.0})
    assert decision.allowed is False
    assert decision.limiting_dimension == "frequency"
    assert decision.max_deviation == 0.19999999999999996

def test_attack_05_untrusted_bool_and_string_flow_values_are_rejected():
    guard = FlowGuard({name: 100.0 for name in ("frequency", "volume", "concurrency", "novelty")})
    base = {name: 100.0 for name in ("frequency", "volume", "concurrency", "novelty")}
    bad_bool = dict(base); bad_bool["frequency"] = True
    with pytest.raises(ValueError, match="numeric int or float"):
        guard.evaluate(bad_bool)
    bad_string = dict(base); bad_string["frequency"] = "125"
    with pytest.raises(ValueError, match="numeric int or float"):
        guard.evaluate(bad_string)
