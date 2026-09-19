from __future__ import annotations

from lat_ces.scientific.evidence_state import EvidenceState
from lat_ces.scientific.core.governance import LifecycleState, ScientificArtifact
from lat_ces.scientific.core.building_adapter import to_building_result


def test_evidence_state_is_explicit_and_independent_from_lifecycle():
    artifact = ScientificArtifact(
        artifact_id="ART-EVIDENCE-001",
        sci_id="LAT-SCI-CORE-0145",
        kind="engineering-result",
        version=1,
        state=LifecycleState.VALIDATED,
        content={"value": 1.0, "unit": "Pa"},
        provenance=("test-source",),
        evidence_state=EvidenceState.MEASURED,
    ).with_hash()

    assert artifact.state is LifecycleState.VALIDATED
    assert artifact.evidence_state is EvidenceState.MEASURED
    assert artifact.state.value != artifact.evidence_state.value


def test_new_revision_downgrades_evidence_state_to_unknown():
    artifact = ScientificArtifact(
        artifact_id="ART-EVIDENCE-002",
        sci_id="LAT-SCI-CORE-0145",
        kind="engineering-result",
        version=1,
        state=LifecycleState.VALIDATED,
        content={"value": 1.0, "unit": "Pa"},
        provenance=("measured:test",),
        evidence_state=EvidenceState.MEASURED,
    ).with_hash()

    from lat_ces.scientific.core.governance import EvolutionEngine
    revised = EvolutionEngine().revise(
        artifact,
        content={"value": 1.1, "unit": "Pa"},
        provenance=("revision:test",),
    )
    assert revised.state is LifecycleState.DRAFT
    assert revised.evidence_state is EvidenceState.UNKNOWN


def test_building_boundary_preserves_evidence_state():
    artifact = ScientificArtifact(
        artifact_id="ART-EVIDENCE-003",
        sci_id="LAT-SCI-CORE-0145",
        kind="engineering-result",
        version=1,
        state=LifecycleState.VALIDATED,
        content={"value": 2.0, "unit": "Pa"},
        provenance=("verified:test",),
        evidence_state=EvidenceState.VERIFIED,
    ).with_hash()
    result = to_building_result(artifact)
    assert result.evidence_state == "VERIFIED"
