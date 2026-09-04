from dataclasses import FrozenInstanceError

import pytest

from lat_ces.structural.restart_reconstruction import (
    ReconstructionEvidence,
    ReconstructedOperationalState,
    RestartReconstructor,
)


def evidence(**overrides):
    values = {
        "decision_ids": ("d1", "d2"),
        "registry_version": "registry-v1",
        "applicability_passed": True,
        "contract_passed": True,
        "selector_version": "selector-v1",
    }
    values.update(overrides)
    return ReconstructionEvidence(**values)


def test_reconstructs_bounded_state_without_activation():
    result = RestartReconstructor().reconstruct(evidence())

    assert isinstance(result, ReconstructedOperationalState)
    assert result.state == "RECONSTRUCTED"
    assert result.decision_ids == ("d1", "d2")


def test_failed_evidence_blocks_reconstruction():
    result = RestartReconstructor().reconstruct(
        evidence(applicability_passed=False)
    )

    assert result.state == "BLOCKED"


def test_contract_failure_blocks_reconstruction():
    result = RestartReconstructor().reconstruct(evidence(contract_passed=False))

    assert result.state == "BLOCKED"


def test_decision_ids_must_be_unique():
    with pytest.raises(ValueError, match="decision_ids must be unique"):
        evidence(decision_ids=("d1", "d1"))


def test_reconstruction_evidence_is_immutable():
    item = evidence()

    with pytest.raises(FrozenInstanceError):
        item.registry_version = "other"


def test_reconstructed_state_is_immutable():
    result = RestartReconstructor().reconstruct(evidence())

    with pytest.raises(FrozenInstanceError):
        result.state = "ACTIVE"


def test_reconstruction_does_not_expose_model_or_selector_objects():
    assert not hasattr(ReconstructionEvidence, "model")
    assert not hasattr(ReconstructedOperationalState, "model")
    assert not hasattr(RestartReconstructor, "selector")
