from lat_ces.rci_ad.flow_observation import FlowObservation
from lat_ces.security.flow_guard import FlowGuard
from lat_ces.security.security_contract import (
    LatcesSecurityContract,
    SecurityAction,
    SecurityRequest,
)


DIMS = ("frequency", "volume", "concurrency", "novelty")


def make_flow(**overrides):
    flow = {name: 100.0 for name in DIMS}
    flow.update(overrides)
    return flow


def test_contract_allows_normal_flow_and_preserves_observation_boundary():
    guard = FlowGuard({name: 100.0 for name in DIMS})
    captured = []
    contract = LatcesSecurityContract(guard, captured.append)

    result = contract.evaluate(
        SecurityRequest("req-1", "kemo.tool.read", make_flow())
    )

    assert result.contract_version == "1.0"
    assert result.decision is SecurityAction.ALLOW
    assert result.flow.allowed is True
    assert len(captured) == 1
    assert guard.baseline == {name: 100.0 for name in DIMS}


def test_contract_denies_hard_stop():
    guard = FlowGuard({name: 100.0 for name in DIMS})
    contract = LatcesSecurityContract(guard, lambda _: None)

    result = contract.evaluate(
        SecurityRequest("req-2", "kemo.tool.write", make_flow(frequency=120.0))
    )

    assert result.decision is SecurityAction.DENY
    assert result.flow.allowed is False
    assert result.limiting_dimension == "frequency"


def test_defense_can_request_review_without_mutating_flowguard():
    guard = FlowGuard({name: 100.0 for name in DIMS})
    captured = []

    def defense(request, observation):
        assert request.action == "kemo.tool.execute"
        assert isinstance(observation, FlowObservation)
        return SecurityAction.REVIEW

    contract = LatcesSecurityContract(guard, captured.append, defense)
    before = guard.baseline

    result = contract.evaluate(
        SecurityRequest("req-3", "kemo.tool.execute", make_flow(frequency=114.0))
    )

    assert result.decision is SecurityAction.REVIEW
    assert result.flow.allowed is True
    assert guard.baseline == before
    assert captured[0].decision == result.flow
