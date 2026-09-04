"""Bounded multi-dimensional flow control for the security boundary.

The guard keeps a fixed trusted baseline and never learns a new baseline from
untrusted traffic.  It starts proportional throttling at 12% deviation and
reaches an admission stop at 20%.  The four dimensions are evaluated in
parallel and the strictest dimension controls the resulting allowance.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping


FLOW_DIMENSIONS = ("frequency", "volume", "concurrency", "novelty")


@dataclass(frozen=True)
class FlowDecision:
    """Fail-closed flow decision for one observation."""

    allowed: bool
    throttle: float
    max_deviation: float
    limiting_dimension: str | None


class FlowGuard:
    """Apply a fixed-baseline, proportional flow limit across four dimensions."""

    START_THROTTLE = 0.12
    HARD_STOP = 0.20

    def __init__(self, baseline: Mapping[str, float]) -> None:
        missing = [name for name in FLOW_DIMENSIONS if name not in baseline]
        extra = [name for name in baseline if name not in FLOW_DIMENSIONS]
        if missing or extra:
            raise ValueError("baseline must contain exactly the four flow dimensions")
        values = {name: float(baseline[name]) for name in FLOW_DIMENSIONS}
        if any(not math.isfinite(value) or value <= 0.0 for value in values.values()):
            raise ValueError("flow baselines must be finite and positive")
        self._baseline = values

    @property
    def baseline(self) -> dict[str, float]:
        """Return a copy; the trusted baseline is immutable after construction."""
        return dict(self._baseline)

    def evaluate(self, observed: Mapping[str, float]) -> FlowDecision:
        """Evaluate all four dimensions; the strongest deviation wins."""
        missing = [name for name in FLOW_DIMENSIONS if name not in observed]
        extra = [name for name in observed if name not in FLOW_DIMENSIONS]
        if missing or extra:
            raise ValueError("observed flow must contain exactly the four dimensions")

        deviations = {}
        for name in FLOW_DIMENSIONS:
            raw_value = observed[name]
            if type(raw_value) not in (int, float):
                raise ValueError("observed flow values must be numeric int or float")
            value = float(raw_value)
            if not math.isfinite(value) or value < 0.0:
                raise ValueError("observed flow values must be finite and non-negative")
            deviations[name] = abs(value / self._baseline[name] - 1.0)

        limiting_dimension = max(deviations, key=deviations.get)
        max_deviation = deviations[limiting_dimension]
        if max_deviation >= self.HARD_STOP:
            return FlowDecision(False, 0.0, max_deviation, limiting_dimension)
        if max_deviation <= self.START_THROTTLE:
            return FlowDecision(True, 1.0, max_deviation, None)

        # Quadratic falloff: the closer to 20%, the more aggressively the pipe closes.
        progress = (max_deviation - self.START_THROTTLE) / (self.HARD_STOP - self.START_THROTTLE)
        throttle = max(0.0, 1.0 - progress * progress)
        return FlowDecision(True, throttle, max_deviation, limiting_dimension)


__all__ = ["FLOW_DIMENSIONS", "FlowDecision", "FlowGuard"]
