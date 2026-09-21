"""HMAC-authenticated IPC envelopes with nonce replay protection."""
from __future__ import annotations

import hashlib
import hmac
import json
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
            stale = [key for key, expires in self._seen.items() if expires <= cutoff]
            for key in stale:
                self._seen.pop(key, None)
            if nonce in self._seen:
                return False
            if len(self._seen) >= self.max_entries:
                oldest = min(self._seen, key=self._seen.get)
                self._seen.pop(oldest, None)
            self._seen[nonce] = current
            return True


class SignedIPCChannel:
    """Authenticated message channel with freshness and replay checking."""

    version = 1

    def __init__(self, shared_secret: bytes | bytearray, *, max_age_seconds: float = 120.0, replay_guard: ReplayGuard | None = None) -> None:
        if not shared_secret:
            raise ValueError("shared secret must be non-empty")
        self._secret = bytes(shared_secret)
        self._max_age = max_age_seconds
        self._replay_guard = replay_guard if replay_guard is not None else ReplayGuard(ttl_seconds=max_age_seconds)

    def pack(self, payload: dict[str, Any], *, sender_id: str) -> bytes:
        if not sender_id:
            raise ValueError("sender_id must be non-empty")
        envelope = {
            "v": self.version,
            "sender_id": sender_id,
            "nonce": secrets.token_hex(16),
            "timestamp": time.time(),
            "payload": payload,
        }
        mac = hmac.new(self._secret, _canonical(envelope), hashlib.sha256).hexdigest()
        return _canonical({"envelope": envelope, "mac": mac})

    def unpack(self, packet: bytes) -> dict[str, Any]:
        try:
            outer = json.loads(packet.decode("utf-8"))
            envelope = outer["envelope"]
            received = outer["mac"]
            if envelope["v"] != self.version:
                raise SecurityError("unsupported IPC envelope version")
            expected = hmac.new(self._secret, _canonical(envelope), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(received, expected):
                raise SecurityError("IPC authentication failed")
            now = time.time()
            timestamp = float(envelope["timestamp"])
            if abs(now - timestamp) > self._max_age:
                raise SecurityError("IPC message expired or timestamp is invalid")
            nonce = str(envelope["nonce"])
            if not self._replay_guard.check_and_add(nonce, now=now):
                raise SecurityError("IPC replay detected")
            return envelope["payload"]
        except SecurityError:
            raise
        except (KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SecurityError("invalid IPC packet") from exc


__all__ = ["ReplayGuard", "SecurityError", "SignedIPCChannel"]
