from __future__ import annotations

import json

import pytest

from lat_ces.security.secure_ipc import SecurityError, SignedIPCChannel


def test_ipc_rejects_oversized_packet() -> None:
    channel = SignedIPCChannel(b"secret")
    packet = channel.pack({"data": "x"}, sender_id="peer")
    assert len(packet) <= channel.max_packet_bytes

    with pytest.raises(SecurityError, match="maximum size"):
        channel.unpack(b"x" * (channel.max_packet_bytes + 1))


def test_ipc_rejects_invalid_sender_identity() -> None:
    channel = SignedIPCChannel(b"secret")

    with pytest.raises(SecurityError, match="sender identity"):
        channel.pack({}, sender_id=" peer")

    with pytest.raises(SecurityError, match="sender identity"):
        channel.pack({}, sender_id="peer\nforged")


def test_ipc_rejects_invalid_nonce_after_authentication() -> None:
    channel = SignedIPCChannel(b"secret")
    packet = channel.pack({}, sender_id="peer")
    decoded = json.loads(packet.decode("utf-8"))
    decoded["envelope"]["nonce"] = "not-a-valid-nonce"

    envelope = decoded["envelope"]
    import hashlib
    import hmac

    decoded["mac"] = hmac.new(
        b"secret",
        json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    with pytest.raises(SecurityError, match="invalid IPC nonce"):
        channel.unpack(json.dumps(decoded, separators=(",", ":")).encode("utf-8"))


def test_replay_identity_is_bound_to_sender() -> None:
    channel = SignedIPCChannel(b"secret")
    packet = channel.pack({"operation": "read"}, sender_id="peer-a")
    decoded = json.loads(packet.decode("utf-8"))

    envelope = decoded["envelope"]
    sender_a_nonce = envelope["nonce"]

    with pytest.raises(SecurityError):
        channel.unpack(packet, expected_sender_id="peer-b")

    assert channel.unpack(packet, expected_sender_id="peer-a") == {"operation": "read"}

    envelope["sender_id"] = "peer-b"
    import hashlib
    import hmac

    decoded["mac"] = hmac.new(
        b"secret",
        json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    with pytest.raises(SecurityError):
        channel.unpack(json.dumps(decoded, separators=(",", ":")).encode("utf-8"), expected_sender_id="peer-b")

    assert sender_a_nonce
