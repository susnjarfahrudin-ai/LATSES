from __future__ import annotations

import pytest

from lat_ces.security.cyber_fortress import CyberFortress
from lat_ces.security.secure_ipc import SecurityError, SignedIPCChannel


def test_sender_identity_must_match_ingress_identity() -> None:
    channel = SignedIPCChannel(b"shared-secret")
    fortress = CyberFortress(channel)

    packet = channel.pack({"operation": "sensitive"}, sender_id="ATTACKER-CLAIMS-ROOT")

    with pytest.raises(SecurityError, match="sender identity mismatch"):
        fortress.receive("10.0.0.1", packet)


def test_matching_sender_identity_reaches_ingress_limiter() -> None:
    channel = SignedIPCChannel(b"shared-secret")
    fortress = CyberFortress(channel)

    packet = channel.pack({"operation": "sensitive"}, sender_id="10.0.0.1")

    assert fortress.receive("10.0.0.1", packet, now=100.0) == {"operation": "sensitive"}
    assert not fortress.rate_limiter.allow("10.0.0.1", now=100.0)
    assert fortress.rate_limiter.allow("different-ingress", now=100.0)
