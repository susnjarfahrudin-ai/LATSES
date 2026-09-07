"""Adversarial proof that an independent FlowGuard oracle detects a broken candidate.

This file is intentionally RED while the candidate uses HARD_STOP=0.21.
It must never be merged in this form. The experiment proves that the oracle
can reject a known mathematical mutation of the FlowGuard model.
"""

from __future__ import annotations

from lat_ces.security.flow_guard import FlowGuard


FLOW_DIMENSIONS = ("frequency", "volume", "concurrency", "novelty")
START_THROTTLE = 0.12
HARD_STOP = 0.20


def independent_oracle(baseline: dict[str, float], observed: dict[str, float]) -> tuple[bool, float, float, str | None]:
    """Calculate the reference result without calling FlowGuard or its helpers."""
    deviations = {
        name: abs(float(observed[name]) / float(baseline[name]) - 1.0)
        for name in FLOW_DIMENSIONS
    }
    limiting_dimension = max(deviations, key=deviations.get)
    max_deviation = deviations[limiting_dimension]

    if max_deviation >= HARD_STOP:
        return False, 0.0, max_deviation, limiting_dimension
    if max_deviation <= START_THROTTLE:
        return True, 1.0, max_deviation, None

    progress = (max_deviation - START_THROTTLE) / (HARD_STOP - START_THROTTLE)
    throttle = max(0.0, 1.0 - progress * progress)
    return True, throttle, max_deviation, limiting_dimension


class BrokenFlowGuard(FlowGuard):
    """Known-bad candidate: moves the hard stop from 20% to 21%."""

    HARD_STOP = 0.21


def test_independent_oracle_rejects_broken_20_percent_boundary() -> None:
    baseline = {
        "frequency": 100.0,
        "volume": 100.0,
        "concurrency": 100.0,
        "novelty": 100.0,
    }
    observed = {
        "frequency": 120.0000001,
        "volume": 100.0,
        "concurrency": 100.0,
        "novelty": 100.0,
    }

    expected = independent_oracle(baseline, observed)
    actual = BrokenFlowGuard(baseline).evaluate(observed)
    actual_tuple = (
        actual.allowed,
        actual.throttle,
        actual.max_deviation,
        actual.limiting_dimension,
    )

    assert expected != actual_tuple
    assert expected[0] is False
    assert actual[0] is True
