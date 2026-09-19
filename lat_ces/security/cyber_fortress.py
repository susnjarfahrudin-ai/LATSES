"""Unified orchestration boundary for existing LAT-CES security primitives."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .adaptive_defense import AdaptiveDefense
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
    """Coordinate canonical security primitives and adaptive defense knowledge."""

    def __init__(self, ipc_channel: SignedIPCChannel, *, rate_limiter: TokenBucketRateLimiter | None = None, threat_engine: ThreatScoreEngine | None = None, adaptive_defense: AdaptiveDefense | None = None) -> None:
        self.ipc = ipc_channel
        self.rate_limiter = rate_limiter if rate_limiter is not None else TokenBucketRateLimiter()
        self.threat = threat_engine if threat_engine is not None else ThreatScoreEngine()
        self.adaptive_defense = adaptive_defense if adaptive_defense is not None else AdaptiveDefense()

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
        except SecurityError as exc:
            self.threat.record(address, 25.0, now=now)
            self.adaptive_defense.observe_failure(
                f"ipc:{str(exc)}",
                "ipc-rejection",
                str(exc),
                source="A",
            )
            raise

    def handoff_verified_defense(self, standby: "CyberFortress") -> int:
        """Copy only explicitly verified defense records to a standby boundary."""
        records = self.adaptive_defense.export_verified()
        for record in records:
            standby.adaptive_defense.import_verified(record)
        return len(records)


__all__ = ["CyberFortress", "SecurityAdmission"]
