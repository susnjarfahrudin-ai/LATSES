"""Versioned LATCES security contract for adapters and action boundaries.

The contract is intentionally narrow: FlowGuard remains the mathematical
admission authority, RCI-AD remains observation-only, and adapters consume a
stable decision record instead of copying internal security state.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Mapping

from lat_ces.rci_ad.flow_observation import FlowObservation, observe_flow
from lat_ces.security.flow_guard import FlowDecision, FlowGuard


class SecurityAction(str, Enum):
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    DENY = "DENY"


@dataclass(frozen=True)
class SecurityRequest:
    request_id: str
    action: str
    flow: Mapping[str, float]


@dataclass(frozen=True)
class SecurityResult:
    contract_version: str
    request_id: str
    action: str
    decision: SecurityAction
    flow: FlowDecision
    limiting_dimension: str | None
    evidence: tuple[str, ...]


class LatcesSecurityContract:
    """Stable boundary: CHECK -> LIMIT -> RCI -> DEFENSE -> decision -> evidence."""

    VERSION = "1.0"

    def __init__(
        self,
        guard: FlowGuard,
        observer: Callable[[FlowObservation], None],
        defense: Callable[[SecurityRequest, FlowObservation], SecurityAction] | None = None,
    ) -> None:
        self._guard = guard
        self._observer = observer
        self._defense = defense

    def evaluate(self, request: SecurityRequest) -> SecurityResult:
        if not request.request_id or not request.action:
            raise ValueError("request_id and action are required")

        observation = observe_flow(
            self._guard,
            request.flow,
            self._observer,
        )
        if not observation.decision.allowed:
            decision = SecurityAction.DENY
        elif self._defense is None:
            decision = SecurityAction.ALLOW
        else:
            decision = self._defense(request, observation)

        evidence = (
            "flowguard",
            "rci-ad-observation-only",
            f"limiting_dimension={observation.limiting_dimension}",
        )
        return SecurityResult(
            contract_version=self.VERSION,
            request_id=request.request_id,
            action=request.action,
            decision=decision,
            flow=observation.decision,
            limiting_dimension=observation.limiting_dimension,
            evidence=evidence,
        )


__all__ = [
    "LatcesSecurityContract",
    "SecurityAction",
    "SecurityRequest",
    "SecurityResult",
]
