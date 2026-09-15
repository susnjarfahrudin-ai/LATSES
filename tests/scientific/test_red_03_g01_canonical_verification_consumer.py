from dataclasses import replace

from lat_ces.scientific.core.knowledge_validation_sci0062_0145 import (
    ScientificClaim,
    ScientificEvidence,
    ScientificKnowledgeValidator,
    ScientificMethod,
)
from lat_ces.scientific.dimensions.dimension import LENGTH
from lat_ces.scientific.governance.authority import Authority
from lat_ces.scientific.governance.governance_engine import ScientificKnowledgeGovernanceEngine
from lat_ces.scientific.models.applicability import ApplicabilityEvaluator, ApplicabilityRequest, ApplicabilityStatus
from lat_ces.scientific.models.contract import ScientificModelContract
from lat_ces.scientific.models.metadata import ModelInput, ModelOutput, ScientificModelMetadata
from lat_ces.scientific.models.registry import ModelRegistry, ModelRegistryEntry, ModelStatus


def _verified_evidence(engine: ScientificKnowledgeGovernanceEngine, evidence_id: str = "E-1") -> tuple[ScientificEvidence, Authority]:
    authority = engine.grant_verification_authority(
        grantor=engine.canonical_root_authority,
        verifier_identity="VERIFIER-1",
        scope="scientific",
        evidence_type="ScientificEvidence",
        domain="Thermodynamics",
        method="sensor-verification-v1",
    )
    candidate = ScientificEvidence(evidence_id, "Experimental", "Sensor campaign", "P-1", "UNKNOWN")
    verified = engine.verify_evidence(
        candidate,
        authority=authority,
        method="sensor-verification-v1",
        criteria="source identity and calibration evidence match",
        reference="CAL-1",
        integrity="HASH-1",
        limitations="sensor uncertainty remains explicit",
        domain="Thermodynamics",
    )
    return verified, authority


def _claim_method() -> tuple[ScientificClaim, ScientificMethod]:
    return (
        ScientificClaim("C-RED03", "Heat transfer depends on temperature difference", "Thermodynamics"),
        ScientificMethod("M-RED03", "Calibrated temperature measurement", (("accuracy", "±0.2°C"),), "Sensor uncertainty remains explicit"),
    )


def _model_registry() -> ModelRegistry:
    metadata = ScientificModelMetadata(
        model_id="MODEL-RED03",
        name="RED-03 test model",
        domain="Thermodynamics",
        description="Minimal model admission fixture",
        equation="y=x",
        inputs=(ModelInput("x", "Input", LENGTH),),
        outputs=(ModelOutput("y", "Output", LENGTH),),
        references=("VERIFICATION_REQUIRED",),
    )
    registry = ModelRegistry()
    registry.register(
        ModelRegistryEntry(
            model_id=metadata.model_id,
            version="1.0",
            status=ModelStatus.ACTIVE,
            metadata=metadata,
            contract=ScientificModelContract(metadata),
        )
    )
    return registry


def _admission_request(evidence: object) -> ApplicabilityRequest:
    return ApplicabilityRequest(
        model_id="MODEL-RED03",
        context={"site": "test"},
        inputs={"x": 1.0},
        evidence={"thermal": evidence},
    )


def test_fake_verification_record_id_is_rejected_by_sci_consumer():
    engine = ScientificKnowledgeGovernanceEngine()
    evidence, _ = _verified_evidence(engine)
    fake = replace(evidence, verification_record_id="FAKE")
    claim, method = _claim_method()
    assert not ScientificKnowledgeValidator(engine).validate(claim, (fake,), method, ("P-1",))


def test_nonexistent_verification_record_is_rejected():
    engine = ScientificKnowledgeGovernanceEngine()
    evidence, _ = _verified_evidence(engine)
    nonexistent = replace(evidence, verification_record_id="VER-NONEXISTENT")
    claim, method = _claim_method()
    assert not ScientificKnowledgeValidator(engine).validate(claim, (nonexistent,), method, ("P-1",))


def test_wrong_evidence_id_is_rejected():
    engine = ScientificKnowledgeGovernanceEngine()
    evidence, _ = _verified_evidence(engine)
    wrong_id = replace(evidence, evidence_id="E-WRONG")
    claim, method = _claim_method()
    assert not ScientificKnowledgeValidator(engine).validate(claim, (wrong_id,), method, ("P-1",))


def test_wrong_evidence_revision_is_rejected():
    engine = ScientificKnowledgeGovernanceEngine()
    evidence, _ = _verified_evidence(engine)
    wrong_revision = replace(evidence, revision=2)
    claim, method = _claim_method()
    assert not ScientificKnowledgeValidator(engine).validate(claim, (wrong_revision,), method, ("P-1",))


def test_revoked_authority_record_is_rejected():
    engine = ScientificKnowledgeGovernanceEngine()
    evidence, authority = _verified_evidence(engine)
    engine.revoke_authority(authority.grant_id, actor=engine.canonical_root_authority)
    claim, method = _claim_method()
    assert not ScientificKnowledgeValidator(engine).validate(claim, (evidence,), method, ("P-1",))


def test_expired_authority_record_is_rejected():
    engine = ScientificKnowledgeGovernanceEngine()
    evidence, authority = _verified_evidence(engine)
    expired = replace(authority, valid_until="2000-01-01T00:00:00+00:00")
    engine.authority_registry._authorities[authority.grant_id] = expired
    engine._authority_grants[authority.grant_id] = expired
    claim, method = _claim_method()
    assert not ScientificKnowledgeValidator(engine).validate(claim, (evidence,), method, ("P-1",))


def test_valid_canonical_verification_record_is_accepted():
    engine = ScientificKnowledgeGovernanceEngine()
    evidence, _ = _verified_evidence(engine)
    claim, method = _claim_method()
    assert ScientificKnowledgeValidator(engine).validate(claim, (evidence,), method, ("P-1",))


def test_model_admission_rejects_fake_verification_record():
    engine = ScientificKnowledgeGovernanceEngine()
    evidence, _ = _verified_evidence(engine)
    fake = replace(evidence, verification_record_id="FAKE")
    result = ApplicabilityEvaluator(_model_registry(), engine).evaluate(_admission_request(fake))
    assert result.status is ApplicabilityStatus.INSUFFICIENT_EVIDENCE
    assert result.applicable is False


def test_model_admission_rejects_wrong_revision():
    engine = ScientificKnowledgeGovernanceEngine()
    evidence, _ = _verified_evidence(engine)
    wrong_revision = replace(evidence, revision=2)
    result = ApplicabilityEvaluator(_model_registry(), engine).evaluate(_admission_request(wrong_revision))
    assert result.status is ApplicabilityStatus.INSUFFICIENT_EVIDENCE
    assert result.applicable is False


def test_model_admission_accepts_valid_canonical_record():
    engine = ScientificKnowledgeGovernanceEngine()
    evidence, _ = _verified_evidence(engine)
    result = ApplicabilityEvaluator(_model_registry(), engine).evaluate(_admission_request(evidence))
    assert result.status is ApplicabilityStatus.APPLICABLE
    assert result.applicable is True


def test_sci_0062_0145_rejects_fake_verification_record():
    engine = ScientificKnowledgeGovernanceEngine()
    evidence, _ = _verified_evidence(engine)
    fake = replace(evidence, verification_record_id="FAKE")
    claim, method = _claim_method()
    assert not ScientificKnowledgeValidator(engine).validate(claim, (fake,), method, ("P-1",))


def test_sci_0062_0145_accepts_valid_canonical_verification_record():
    engine = ScientificKnowledgeGovernanceEngine()
    evidence, _ = _verified_evidence(engine)
    claim, method = _claim_method()
    assert ScientificKnowledgeValidator(engine).validate(claim, (evidence,), method, ("P-1",))


def test_canonical_resolver_rejects_record_bound_to_wrong_revision():
    engine = ScientificKnowledgeGovernanceEngine()
    evidence, _ = _verified_evidence(engine)
    record = engine.get_verification_record(evidence.verification_record_id)
    assert engine.resolve_verification_record(
        record.record_id,
        evidence_id=record.evidence_id,
        evidence_revision=record.evidence_revision + 1,
        evidence_type=record.evidence_type,
    ) is None


def test_canonical_resolver_rejects_record_bound_to_wrong_evidence():
    engine = ScientificKnowledgeGovernanceEngine()
    evidence, _ = _verified_evidence(engine)
    record = engine.get_verification_record(evidence.verification_record_id)
    assert engine.resolve_verification_record(
        record.record_id,
        evidence_id="OTHER-EVIDENCE",
        evidence_revision=record.evidence_revision,
        evidence_type=record.evidence_type,
    ) is None
