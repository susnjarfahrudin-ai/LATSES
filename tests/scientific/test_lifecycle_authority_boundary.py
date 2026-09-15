import pytest

from lat_ces.scientific.lifecycle.lifecycle_engine import (
    LifecycleTransitionEngine,
    ScientificKnowledgeLifecycleEngine,
    ScientificKnowledgeLifecycleObject,
)


def test_lifecycle_state_cannot_be_assigned_directly():
    with pytest.raises(ValueError, match="LifecycleTransitionEngine"):
        ScientificKnowledgeLifecycleObject("K-1", state="VALIDATED")


def test_lifecycle_transition_engine_is_the_authorized_promotion_path():
    obj = ScientificKnowledgeLifecycleEngine().create("K-1")
    transitioned = LifecycleTransitionEngine().transition(obj, "DOCUMENTED", "2026-09-14T22:00:00+00:00")
    assert transitioned.state == "DOCUMENTED"
    assert transitioned.history[-1].state == "DOCUMENTED"
