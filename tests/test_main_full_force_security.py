"""Forensic attack tests against the current main security boundary.

These tests intentionally assert security properties that the current
implementation may not yet satisfy. A failing test is evidence of a concrete
boundary gap; production code is not modified by this test module.
"""
from __future__ import annotations

import pytest

from lat_ces.security.adaptive_defense import AdaptiveDefense
from lat_ces.security.cyber_fortress import CyberFortress
from lat_ces.security.secure_ipc import SecurityError, SignedIPCChannel, ReplayGuard


def test_sender_identity_cannot_be_self_declared_at_ingress() -> None:
    """Attack: a sender claim cannot override the trusted ingress identity."""
    channel = SignedIPCChannel(b"shared-secret")
    fortress = CyberFortress(channel)
    packet = channel.pack({"operation": "sensitive"}, sender_id="ATTACKER-CLAIMS-ROOT")
    with pytest.raises(SecurityError, match="sender identity mismatch"):
        fortress.receive("10.0.0.1", packet, now=100.0)


def test_compromised_peer_cannot_impersonate_another_peer_at_boundary() -> None:
    """Attack: a peer identity claim cannot cross a trusted peer boundary."""
    channel = SignedIPCChannel(b"shared-secret")
    packet_from_a = channel.pack({"operation": "sensitive"}, sender_id="PEER-A")
    with pytest.raises(SecurityError, match="sender identity mismatch"):
        channel.unpack(packet_from_a, expected_sender_id="PEER-B")


def test_replay_guard_preserves_replay_detection_under_pressure() -> None:
    """Attack: nonce pressure must not make an accepted nonce valid again."""
    guard = ReplayGuard(ttl_seconds=120, max_entries=32)
    assert guard.check_and_add("victim", now=100.0)
    for index in range(1000):
        assert guard.check_and_add(f"nonce-{index}", now=100.0)
    assert not guard.check_and_add("victim", now=100.0)


def test_quarantine_is_an_enforced_runtime_boundary() -> None:
    """Attack: quarantining a defense record must prevent protected runtime use."""
    defense = AdaptiveDefense()
    record = defense.observe_failure(
        "ipc:authentication-failed",
        "ipc-rejection",
        "forensic attack",
    )
    defense.quarantine(record)
    assert defense.is_quarantined(record.invariant_id)

    fortress = CyberFortress(SignedIPCChannel(b"shared-secret"), adaptive_defense=defense)
    packet = fortress.ipc.pack({"operation": "sensitive"}, sender_id="trusted")
    with pytest.raises(SecurityError):
        fortress.receive("10.0.0.1", packet, now=100.0)


def test_quarantine_control_pair_is_not_masked_by_ipc_identity_failure() -> None:
    """Attack: the same valid packet must pass normally and fail only if quarantine is enforced."""
    channel = SignedIPCChannel(b"shared-secret")
    address = "10.0.0.1"
    packet = channel.pack({"operation": "sensitive"}, sender_id=address)

    baseline = CyberFortress(channel)
    assert baseline.receive(address, packet, now=100.0) == {"operation": "sensitive"}

    defense = AdaptiveDefense()
    record = defense.observe_failure(
        "ipc:authentication-failed",
        "ipc-rejection",
        "forensic attack",
    )
    defense.quarantine(record)

    quarantined = CyberFortress(channel, adaptive_defense=defense)
    with pytest.raises(SecurityError, match="quarantined"):
        quarantined.receive(address, packet, now=100.0)
