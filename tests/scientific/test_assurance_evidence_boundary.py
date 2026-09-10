from lat_ces.scientific.core.governance import AssuranceEngine, LifecycleState, ScientificArtifact
from lat_ces.scientific.evidence_state import EvidenceState


def _artifact(evidence_state: EvidenceState) -> ScientificArtifact:
    return ScientificArtifact(
        artifact_id="A-ASSURANCE-1",
        sci_id="SCI-145",
        kind="engineering-result",
        version=1,
        state=LifecycleState.VALIDATED,
        content={"result": 42},
        provenance=("SRC-1",),
        evidence_state=evidence_state,
    ).with_hash()


def test_assurance_cannot_be_high_when_evidence_is_unknown():
    result = AssuranceEngine().assess(_artifact(EvidenceState.UNKNOWN))

    assert result.level == "LOW"
    assert "evidence not verified/measured" in result.reasons


def test_verified_or_measured_evidence_can_support_high_assurance():
    engine = AssuranceEngine()

    verified = engine.assess(_artifact(EvidenceState.VERIFIED))
    measured = engine.assess(_artifact(EvidenceState.MEASURED))

    assert verified.level == "HIGH"
    assert measured.level == "HIGH"
