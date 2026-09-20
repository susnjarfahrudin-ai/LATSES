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


def test_sender_identity_cannot_be_self_declared() -> None:
    """Attack: a holder of the shared secret claims an arbitrary sender identity."""
    channel = SignedIPCChannel(b"shared-secret")
    packet = channel.pack({"operation": "sensitive"}, sender_id="ATTACKER-CLAIMS-ROOT")
    with pytest.raises(SecurityError):
        channel.unpack(packet)


def test_compromised_peer_cannot_impersonate_another_peer() -> None:
    """Attack: peers using one shared secret must not be able to cross-impersonate."""
    peer_a = SignedIPCChannel(b"shared-secret")
    peer_b = SignedIPCChannel(b"shared-secret")
    packet_from_a = peer_a.pack({"operation": "sensitive"}, sender_id="PEER-A")
    decoded = peer_b.unpack(packet_from_a)
    assert decoded is None, "shared-secret packet must not authenticate PEER-A to PEER-B"


def test_replay_guard_enforces_declared_memory_bound() -> None:
    """Attack: unique authenticated nonces must not grow state beyond max_entries."""
    guard = ReplayGuard(ttl_seconds=120, max_entries=32)
    for index in range(1000):
        assert guard.check_and_add(f"nonce-{index}", now=100.0)
    assert len(guard._seen) <= guard.max_entries


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
