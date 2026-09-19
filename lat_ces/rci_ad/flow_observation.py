"""Observation-only bridge from the mathematical FlowGuard into RCI-AD.

This module reads a FlowGuard decision and forwards one immutable observation
record to a caller-supplied observer. It does not change the guard, limiter,
policy thresholds, admission result, or any runtime security state.
"""
from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Callable, Mapping

from lat_ces.security.flow_guard import FLOW_DIMENSIONS, FlowDecision, FlowGuard


@dataclass(frozen=True)
class FlowObservation:
    """Immutable record of one mathematical flow evaluation."""

    timestamp: float
    baseline: tuple[tuple[str, float], ...]
    observed: tuple[tuple[str, float], ...]
    decision: FlowDecision

    @property
    def limiting_dimension(self) -> str | None:
        return self.decision.limiting_dimension


FlowObserver = Callable[[FlowObservation], None]


def observe_flow(
    guard: FlowGuard,
    observed: Mapping[str, float],
    observer: FlowObserver,
    *,
    timestamp: float | None = None,
) -> FlowObservation:
    """Evaluate the existing guard, then forward exactly one read-only record."""
    decision = guard.evaluate(observed)
    observation = FlowObservation(
        timestamp=time.time() if timestamp is None else timestamp,
        baseline=tuple((name, guard.baseline[name]) for name in FLOW_DIMENSIONS),
        observed=tuple((name, float(observed[name])) for name in FLOW_DIMENSIONS),
        decision=decision,
    )
    observer(observation)
    return observation


__all__ = ["FlowObservation", "FlowObserver", "observe_flow"]
