"""Independent mathematical oracle and adversarial falsification proof."""

from __future__ import annotations

import pytest

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


def _case() -> tuple[dict[str, float], dict[str, float]]:
    return (
        {
            "frequency": 100.0,
            "volume": 100.0,
            "concurrency": 100.0,
            "novelty": 100.0,
        },
        {
            "frequency": 120.0000001,
            "volume": 100.0,
            "concurrency": 100.0,
            "novelty": 100.0,
        },
    )


def test_independent_oracle_rejects_broken_20_percent_boundary() -> None:
    """Falsification witness: a 21% hard stop disagrees with the oracle."""
    baseline, observed = _case()
    expected = independent_oracle(baseline, observed)

    class BrokenFlowGuard(FlowGuard):
        HARD_STOP = 0.21

    actual = BrokenFlowGuard(baseline).evaluate(observed)
    actual_tuple = (
        actual.allowed,
        actual.throttle,
        actual.max_deviation,
        actual.limiting_dimension,
    )

    assert expected != actual_tuple
    assert expected[0] is False
    assert actual.allowed is True


def test_canonical_flowguard_converges_with_independent_oracle() -> None:
    """Canonical FlowGuard must agree with the independent oracle."""
    baseline, observed = _case()
    expected = independent_oracle(baseline, observed)
    actual = FlowGuard(baseline).evaluate(observed)

    assert actual.allowed is expected[0]
    assert actual.throttle == pytest.approx(expected[1])
    assert actual.max_deviation == pytest.approx(expected[2])
    assert actual.limiting_dimension == expected[3]
