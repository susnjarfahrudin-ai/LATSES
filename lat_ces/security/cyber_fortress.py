"""Unified orchestration boundary for existing LAT-CES security primitives.

This module intentionally contains policy orchestration only. Cryptographic,
process, memory, persistence, rate-limit, replay, and threat-score primitives
remain owned by their canonical modules.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .process_security import ProcessIdentity, ProcessIsolationResult, activate_process_isolation, current_process_identity
from .rate_limit import TokenBucketRateLimiter
from .secure_ipc import SecurityError, SignedIPCChannel
from .threat_score import ThreatScoreEngine


@dataclass(frozen=True)
class SecurityAdmission:
    """Decision returned by the unified request boundary."""

    allowed: bool
    reason: str
    threat_score: float


class CyberFortress:
    """Coordinate existing security primitives at one runtime boundary."""

    def __init__(self, ipc_channel: SignedIPCChannel, *, rate_limiter: TokenBucketRateLimiter | None = None, threat_engine: ThreatScoreEngine | None = None) -> None:
        self.ipc = ipc_channel
        self.rate_limiter = rate_limiter if rate_limiter is not None else TokenBucketRateLimiter()
        self.threat = threat_engine if threat_engine is not None else ThreatScoreEngine()

    @staticmethod
    def establish_process_boundary(*, strict: bool = False) -> ProcessIsolationResult:
        return activate_process_isolation(strict=strict)

    @staticmethod
    def process_identity() -> ProcessIdentity:
        return current_process_identity()

    def admit(self, address: str, *, cost: float = 1.0, now: float | None = None) -> SecurityAdmission:
        if self.threat.should_block(address, now=now):
            score = self.threat.score(address, now=now)
            return SecurityAdmission(False, "threat-blocked", score)
        if not self.rate_limiter.allow(address, now=now, cost=cost):
            score = self.threat.record(address, 10.0, now=now)
            return SecurityAdmission(False, "rate-limited", score)
        return SecurityAdmission(True, "allowed", self.threat.score(address, now=now))

    def receive(self, address: str, packet: bytes, *, cost: float = 1.0, now: float | None = None) -> dict[str, Any]:
        admission = self.admit(address, cost=cost, now=now)
        if not admission.allowed:
            raise SecurityError(admission.reason)
        try:
            return self.ipc.unpack(packet)
        except SecurityError:
            self.threat.record(address, 25.0, now=now)
            raise


__all__ = ["CyberFortress", "SecurityAdmission"]
