"""Deterministic token-bucket admission control for the security boundary."""
from __future__ import annotations

from dataclasses import dataclass, field
import threading
import time


@dataclass
class TokenBucket:
    capacity: float
    refill_per_second: float
    tokens: float | None = None
    updated_at: float | None = None

    def __post_init__(self) -> None:
        if self.capacity <= 0 or self.refill_per_second <= 0:
            raise ValueError("capacity and refill_per_second must be positive")
        if self.tokens is None:
            self.tokens = self.capacity
        else:
            self.tokens = min(self.capacity, max(0.0, self.tokens))
        if self.updated_at is None:
            self.updated_at = time.monotonic()

    def allow(self, *, now: float | None = None, cost: float = 1.0) -> bool:
        if cost <= 0:
            raise ValueError("cost must be positive")
        current = time.monotonic() if now is None else now
        elapsed = max(0.0, current - self.updated_at)
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_second)
        self.updated_at = current
        if self.tokens < cost:
            return False
        self.tokens -= cost
        return True


class TokenBucketRateLimiter:
    """Per-key token buckets with bounded idle cleanup."""

    def __init__(self, *, capacity: float = 5.0, refill_per_second: float = 1.0, idle_ttl_seconds: float = 300.0) -> None:
        if idle_ttl_seconds <= 0:
            raise ValueError("idle_ttl_seconds must be positive")
        self.capacity = capacity
        self.refill_per_second = refill_per_second
        self.idle_ttl_seconds = idle_ttl_seconds
        self._buckets: dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def allow(self, key: str, *, now: float | None = None, cost: float = 1.0) -> bool:
        if not key:
            raise ValueError("key must be non-empty")
        current = time.monotonic() if now is None else now
        with self._lock:
            self._evict_idle(current)
            bucket = self._buckets.get(key)
            if bucket is None:
                bucket = TokenBucket(self.capacity, self.refill_per_second, updated_at=current)
                self._buckets[key] = bucket
            return bucket.allow(now=current, cost=cost)

    def _evict_idle(self, now: float) -> None:
        cutoff = now - self.idle_ttl_seconds
        stale = [key for key, bucket in self._buckets.items() if bucket.updated_at < cutoff]
        for key in stale:
            self._buckets.pop(key, None)


__all__ = ["TokenBucket", "TokenBucketRateLimiter"]
