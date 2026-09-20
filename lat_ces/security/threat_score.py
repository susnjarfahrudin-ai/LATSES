"""Time-decaying threat scores with signed immutable network allowlists."""
from __future__ import annotations

import ipaddress
import math
import threading
import time
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ThreatScorePolicy:
    decay_window_seconds: float = 300.0
    max_score: float = 100.0
    block_threshold: float = 75.0
    whitelist: tuple[str, ...] = ("127.0.0.0/8", "::1/128")

    def __post_init__(self) -> None:
        if self.decay_window_seconds <= 0:
            raise ValueError("decay_window_seconds must be positive")
        if self.max_score <= 0 or self.block_threshold <= 0:
            raise ValueError("score bounds must be positive")
        normalized = tuple(str(ipaddress.ip_network(item, strict=False)) for item in self.whitelist)
        object.__setattr__(self, "whitelist", normalized)

    @staticmethod
    def _extract_ip(address: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
        """Return the IP component of an ingress identity, when it is one.

        Security state is keyed by the original identity string, but the
        network whitelist is an IP-only policy. Accepted forms are bare IPv4,
        bare IPv6, IPv4:port, and [IPv6]:port. Non-IP identities are simply
        not whitelistable rather than being treated as malformed requests.
        """
        if not isinstance(address, str) or not address:
            return None

        candidate = address
        if address.startswith("["):
            close = address.find("]")
            if close <= 1:
                return None
            candidate = address[1:close]
            suffix = address[close + 1 :]
            if suffix and (not suffix.startswith(":") or not suffix[1:].isdigit()):
                return None
        elif address.count(":") == 1:
            host, port = address.rsplit(":", 1)
            if host and port.isdigit():
                candidate = host

        try:
            return ipaddress.ip_address(candidate)
        except ValueError:
            return None

    def is_whitelisted(self, address: str) -> bool:
        ip = self._extract_ip(address)
        if ip is None:
            return False
        return any(ip in ipaddress.ip_network(network) for network in self.whitelist)


class ThreatScoreEngine:
    """In-memory score store; persistence/signing belongs to the constitutional registry."""

    def __init__(self, policy: ThreatScorePolicy | None = None) -> None:
        self.policy = policy if policy is not None else ThreatScorePolicy()
        self._scores: dict[str, tuple[float, float]] = {}
        self._lock = threading.Lock()

    def _decay(self, score: float, elapsed: float) -> float:
        if elapsed <= 0:
            return score
        return score / (1.0 + math.log1p(elapsed / self.policy.decay_window_seconds))

    def score(self, address: str, *, now: float | None = None) -> float:
        if self.policy.is_whitelisted(address):
            return 0.0
        current = time.time() if now is None else now
        with self._lock:
            score, updated = self._scores.get(address, (0.0, current))
            return min(self.policy.max_score, max(0.0, self._decay(score, current - updated)))

    def record(self, address: str, points: float, *, now: float | None = None) -> float:
        if points < 0:
            raise ValueError("points must be non-negative")
        if self.policy.is_whitelisted(address):
            return 0.0
        current = time.time() if now is None else now
        with self._lock:
            old_score, updated = self._scores.get(address, (0.0, current))
            score = self._decay(old_score, current - updated)
            score = min(self.policy.max_score, score + points)
            self._scores[address] = (score, current)
            return score

    def should_block(self, address: str, *, now: float | None = None) -> bool:
        return (not self.policy.is_whitelisted(address)) and self.score(address, now=now) >= self.policy.block_threshold

    def export_scores(self, addresses: Iterable[str]) -> dict[str, float]:
        return {address: self.score(address) for address in addresses}


__all__ = ["ThreatScoreEngine", "ThreatScorePolicy"]
