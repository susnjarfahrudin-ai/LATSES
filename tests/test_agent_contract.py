import pytest

from lat_ces.agent_contract import (
    AgentAuthority,
    SciTask,
    assign_replacement,
    can_execute,
    revoke,
)


def task():
    return SciTask(
        "SCI-001",
        "task-material-check",
        "suljo",
        "material.review",
        "material-catalog boundary",
        "material has all required elements",
        "omer",
    )


def test_agent_can_execute_only_granted_capability():
    assert can_execute(task(), AgentAuthority(frozenset({"material.review"})))
    assert not can_execute(task(), AgentAuthority(frozenset({"acoustic.review"})))


def test_authority_is_revoked_without_mutating_original():
    authority = AgentAuthority(frozenset({"material.review", "material.read"}))
    reduced = revoke(authority, "material.review")
    assert authority.allows("material.review")
    assert not reduced.allows("material.review")
    assert reduced.allows("material.read")


def test_replacement_preserves_contract_but_changes_owner():
    replacement = assign_replacement(task(), "mladi-hase")
    assert replacement.owner == "mladi-hase"
    assert replacement.sci_id == "SCI-001"
    assert replacement.invariant == task().invariant
    assert replacement.verifier == "omer"


def test_owner_cannot_be_verifier():
    with pytest.raises(ValueError):
        SciTask("SCI-001", "task", "suljo", "review", "boundary", "invariant", "suljo")


def test_replacement_cannot_be_verifier():
    with pytest.raises(ValueError):
        assign_replacement(task(), "omer")
