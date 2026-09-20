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
        json.dumps(
            envelope,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    with pytest.raises(SecurityError, match="invalid IPC nonce"):
        channel.unpack(json.dumps(decoded, separators=(",", ":")).encode("utf-8"))


def test_replay_key_is_namespaced_by_authenticated_sender() -> None:
    channel = SignedIPCChannel(b"secret")
    packet_a = channel.pack({"operation": "read"}, sender_id="peer-a")
    decoded_a = json.loads(packet_a.decode("utf-8"))
    nonce = decoded_a["envelope"]["nonce"]

    assert channel.unpack(packet_a, expected_sender_id="peer-a") == {"operation": "read"}

    envelope_b = dict(decoded_a["envelope"])
    envelope_b["sender_id"] = "peer-b"

    import hashlib
    import hmac

    mac_b = hmac.new(
        b"secret",
        json.dumps(
            envelope_b,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    packet_b = json.dumps(
        {"envelope": envelope_b, "mac": mac_b},
        separators=(",", ":"),
    ).encode("utf-8")

    # The same nonce is independently tracked for each authenticated sender.
    # A replay from peer-a remains rejected.
    with pytest.raises(SecurityError, match="replay"):
        channel.unpack(packet_a, expected_sender_id="peer-a")

    # The peer-b packet is a distinct authenticated envelope and therefore
    # does not inherit peer-a's replay state.
    assert channel.unpack(packet_b, expected_sender_id="peer-b") == {"operation": "read"}
    assert nonce
