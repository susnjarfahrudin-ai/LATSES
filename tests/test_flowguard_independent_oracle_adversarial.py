"""Independent mathematical witness, falsification proof, and convergence test."""

from __future__ import annotations

from decimal import Decimal

import pytest

from lat_ces.security.flow_guard import FlowGuard


def independent_witness() -> tuple[bool, float, float, str]:
    """Derive one exact hard-stop result without reproducing FlowGuard.evaluate().

    The witness uses exact decimal arithmetic for the specific adversarial case:
    120.0000001 / 100 - 1 = 0.200000001 > 0.20.
    """
    baseline = Decimal("100")
    observed = Decimal("120.0000001")
    deviation = abs(observed / baseline - Decimal("1"))
    assert deviation > Decimal("0.20")
    return False, 0.0, float(deviation), "frequency"


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


def test_independent_oracle_rejects_broken_hard_stop() -> None:
    """Falsification witness: a 21% hard stop disagrees with the 20% contract."""
    baseline, observed = _case()
    expected = independent_witness()

    class BrokenFlowGuard(FlowGuard):
        HARD_STOP = 0.21

    actual = BrokenFlowGuard(baseline).evaluate(observed)
    assert expected[0] is False
    assert actual.allowed is True
    assert actual.throttle > expected[1]
    assert actual.max_deviation == pytest.approx(expected[2])
    assert actual.limiting_dimension == expected[3]


def test_canonical_flowguard_converges_with_independent_oracle() -> None:
    """Canonical FlowGuard must agree with the independently derived witness."""
    baseline, observed = _case()
    expected = independent_witness()
    actual = FlowGuard(baseline).evaluate(observed)

    assert actual.allowed is expected[0]
    assert actual.throttle == expected[1]
    assert actual.max_deviation == pytest.approx(expected[2])
    assert actual.limiting_dimension == expected[3]
