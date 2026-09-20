"""HMAC-authenticated IPC envelopes with nonce replay protection."""
from __future__ import annotations

import hashlib
import hmac
import json
import math
import secrets
import threading
import time
from dataclasses import dataclass, field
from typing import Any


class SecurityError(ValueError):
    """Raised when an IPC security invariant fails."""


def _canonical(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


@dataclass
class ReplayGuard:
    ttl_seconds: float = 120.0
    max_entries: int = 100_000
    _seen: dict[str, float] = field(default_factory=dict, init=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def check_and_add(self, nonce: str, *, now: float | None = None) -> bool:
        current = time.time() if now is None else now
        if self.ttl_seconds <= 0 or self.max_entries <= 0:
            raise ValueError("invalid replay guard policy")
        with self._lock:
            cutoff = current - self.ttl_seconds
            stale = [key for key, seen_at in self._seen.items() if seen_at <= cutoff]
            for key in stale:
                self._seen.pop(key, None)
            if nonce in self._seen:
                return False
            self._seen[nonce] = current
            return True


class SignedIPCChannel:
    """Authenticated message channel with freshness, identity and replay checking."""

    version = 1
    max_packet_bytes = 1_048_576
    max_sender_id_length = 256
    nonce_hex_length = 32

    def __init__(
        self,
        shared_secret: bytes | bytearray,
        *,
        max_age_seconds: float = 120.0,
        max_future_skew_seconds: float = 5.0,
        replay_guard: ReplayGuard | None = None,
    ) -> None:
        if not shared_secret:
            raise ValueError("shared secret must be non-empty")
        if max_age_seconds <= 0 or max_future_skew_seconds < 0:
            raise ValueError("invalid IPC freshness policy")
        self._secret = bytes(shared_secret)
        self._max_age = max_age_seconds
        self._max_future_skew = max_future_skew_seconds
        self._replay_guard = replay_guard if replay_guard is not None else ReplayGuard(ttl_seconds=max_age_seconds)

    @classmethod
    def _validate_sender_id(cls, sender_id: Any) -> str:
        if not isinstance(sender_id, str) or not sender_id:
            raise SecurityError("invalid IPC sender identity")
        if len(sender_id) > cls.max_sender_id_length:
            raise SecurityError("invalid IPC sender identity")
        if sender_id != sender_id.strip() or any(ord(ch) < 0x20 for ch in sender_id):
            raise SecurityError("invalid IPC sender identity")
        return sender_id

    @classmethod
    def _validate_nonce(cls, nonce: Any) -> str:
        if not isinstance(nonce, str) or len(nonce) != cls.nonce_hex_length:
            raise SecurityError("invalid IPC nonce")
        try:
            int(nonce, 16)
        except ValueError as exc:
            raise SecurityError("invalid IPC nonce") from exc
        return nonce

    def pack(self, payload: dict[str, Any], *, sender_id: str) -> bytes:
        self._validate_sender_id(sender_id)
        if not isinstance(payload, dict):
            raise ValueError("payload must be a dictionary")
        envelope = {
            "v": self.version,
            "sender_id": sender_id,
            "nonce": secrets.token_hex(16),
            "timestamp": time.time(),
            "payload": payload,
        }
        mac = hmac.new(self._secret, _canonical(envelope), hashlib.sha256).hexdigest()
        return _canonical({"envelope": envelope, "mac": mac})

    def unpack(self, packet: bytes, *, expected_sender_id: str | None = None) -> dict[str, Any]:
        try:
            if not isinstance(packet, (bytes, bytearray)):
                raise SecurityError("invalid IPC packet")
            if len(packet) > self.max_packet_bytes:
                raise SecurityError("IPC packet exceeds maximum size")
            outer = json.loads(bytes(packet).decode("utf-8"))
            if not isinstance(outer, dict):
                raise SecurityError("invalid IPC packet")
            envelope = outer["envelope"]
            received = outer["mac"]
            if not isinstance(envelope, dict) or not isinstance(received, str):
                raise SecurityError("invalid IPC packet")
            if len(received) != hashlib.sha256().digest_size * 2:
                raise SecurityError("IPC authentication failed")
            try:
                int(received, 16)
            except ValueError as exc:
                raise SecurityError("IPC authentication failed") from exc
            if envelope["v"] != self.version:
                raise SecurityError("unsupported IPC envelope version")
            expected = hmac.new(self._secret, _canonical(envelope), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(received, expected):
                raise SecurityError("IPC authentication failed")
            sender_id = self._validate_sender_id(envelope["sender_id"])
            if expected_sender_id is not None:
                self._validate_sender_id(expected_sender_id)
                if not hmac.compare_digest(sender_id, expected_sender_id):
                    raise SecurityError("IPC sender identity mismatch")
            now = time.time()
            timestamp = float(envelope["timestamp"])
            if not math.isfinite(timestamp):
                raise SecurityError("IPC message expired or timestamp is invalid")
            age = now - timestamp
            if age > self._max_age or age < -self._max_future_skew:
                raise SecurityError("IPC message expired or timestamp is invalid")
            nonce = self._validate_nonce(envelope["nonce"])
            replay_key = f"{sender_id}:{nonce}"
            if not self._replay_guard.check_and_add(replay_key, now=now):
                raise SecurityError("IPC replay detected")
            payload = envelope["payload"]
            if not isinstance(payload, dict):
                raise SecurityError("invalid IPC payload")
            return payload
        except SecurityError:
            raise
        except (KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SecurityError("invalid IPC packet") from exc


__all__ = ["ReplayGuard", "SecurityError", "SignedIPCChannel"]
