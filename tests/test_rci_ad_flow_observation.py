from lat_ces.rci_ad.flow_observation import observe_flow
from lat_ces.security.flow_guard import FlowGuard


def test_flow_observation_forwards_exact_mathematical_decision() -> None:
    guard = FlowGuard({name: 100.0 for name in ("frequency", "volume", "concurrency", "novelty")})
    observed = {name: 100.0 for name in guard.baseline}
    observed["frequency"] = 119.9
    captured = []

    result = observe_flow(guard, observed, captured.append, timestamp=123.0)

    assert result is captured[0]
    assert result.timestamp == 123.0
    assert result.decision.allowed is True
    assert result.decision.limiting_dimension == "frequency"
    assert result.decision.max_deviation == 0.199
    assert result.decision.throttle > 0.0
    assert result.baseline == tuple((name, 100.0) for name in guard.baseline)
    assert result.observed == (
        ("frequency", 119.9),
        ("volume", 100.0),
        ("concurrency", 100.0),
        ("novelty", 100.0),
    )


def test_rci_observation_does_not_change_guard_state_or_decision() -> None:
    guard = FlowGuard({name: 100.0 for name in ("frequency", "volume", "concurrency", "novelty")})
    before = guard.baseline
    observed = {name: 100.0 for name in before}
    observed["frequency"] = 124.9
    captured = []

    observation = observe_flow(guard, observed, captured.append)
    repeat = guard.evaluate(observed)

    assert observation.decision == repeat
    assert guard.baseline == before
    assert len(captured) == 1
    assert captured[0].decision == repeat


def test_all_four_dimensions_are_preserved_for_rcia_analysis() -> None:
    guard = FlowGuard({name: 100.0 for name in ("frequency", "volume", "concurrency", "novelty")})
    observed = {
        "frequency": 100.0,
        "volume": 100.0,
        "concurrency": 114.9,
        "novelty": 100.0,
    }
    captured = []

    observation = observe_flow(guard, observed, captured.append)

    assert observation.limiting_dimension == "concurrency"
    assert observation.decision.max_deviation == 0.149
    assert all(name in dict(observation.observed) for name in guard.baseline)
