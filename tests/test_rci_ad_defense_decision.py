import pytest

from lat_ces.rci_ad.defense_decision import DefenseAction, DefenseDecision


@pytest.mark.parametrize(
    "action",
    [
        DefenseAction.ALLOW,
        DefenseAction.OBSERVE,
        DefenseAction.THROTTLE,
        DefenseAction.DROP,
        DefenseAction.ISOLATE,
        DefenseAction.RECOVER,
    ],
)
def test_all_canonical_defense_actions_are_representable(action):
    decision = DefenseDecision(
        action=action,
        reason="test",
        source_id="flowguard",
        sequence=1,
    )
    assert decision.action is action


def test_defense_decision_is_immutable():
    decision = DefenseDecision(
        action=DefenseAction.OBSERVE,
        reason="observation only",
        source_id="flowguard",
        sequence=1,
    )
    with pytest.raises(Exception):
        decision.action = DefenseAction.DROP


@pytest.mark.parametrize(
    "field,value",
    [
        ("reason", ""),
        ("source_id", ""),
        ("sequence", -1),
        ("sequence", True),
    ],
)
def test_invalid_decision_identity_and_sequence_are_rejected(field, value):
    with pytest.raises(ValueError):
        DefenseDecision(
            action=DefenseAction.OBSERVE,
            reason="reason",
            source_id="flowguard",
            sequence=1,
            **{field: value},
        )


def test_invalid_action_is_rejected():
    with pytest.raises(ValueError):
        DefenseDecision(
            action="DROP",
            reason="reason",
            source_id="flowguard",
            sequence=1,
        )


def test_decision_contract_has_no_enforcement_side_effect():
    decision = DefenseDecision(
        action=DefenseAction.ISOLATE,
        reason="verified threat",
        source_id="flowguard",
        sequence=2,
    )
    assert decision.action is DefenseAction.ISOLATE
