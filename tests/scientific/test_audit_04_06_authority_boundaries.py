import pytest

from lat_ces.scientific.core.knowledge_validation_sci0062_0145 import ScientificEvidence
from lat_ces.scientific.governance.approval import ApprovalWorkflow
from lat_ces.scientific.governance.authority import Authority
from lat_ces.scientific.governance.governance_engine import ScientificKnowledgeGovernanceEngine
from lat_ces.scientific.measurement.evidence import MeasurementEvidence


def _grantor() -> Authority:
    return Authority(
        identity="CONSTITUTION",
        level=3,
        scope="*",
        action="GRANT_VERIFICATION_AUTHORITY",
        grant_id="ROOT-GRANT",
        grantor="LAT-CONSTITUTION",
    )


def _engine_and_verifier() -> tuple[ScientificKnowledgeGovernanceEngine, Authority]:
    engine = ScientificKnowledgeGovernanceEngine()
    verifier = engine.grant_verification_authority(
        grantor=_grantor(),
        verifier_identity="VERIFIER-1",
        scope="measurement",
        evidence_type="MeasurementEvidence",
        domain="thermal",
        method="sensor-check-v1",
    )
    return engine, verifier


def test_verifier_cannot_self_grant():
    with pytest.raises(ValueError, match="grant authority to itself"):
        Authority(
            identity="SELF",
            level=3,
            scope="*",
            action="GRANT_VERIFICATION_AUTHORITY",
            grant_id="SELF-GRANT",
            grantor="SELF",
        )


def test_direct_verified_scientific_evidence_is_rejected():
    with pytest.raises(ValueError, match="verification record"):
        ScientificEvidence(
            evidence_id="E-1",
            evidence_type="MeasurementEvidence",
            source="sensor",
            provenance_id="P-1",
            integrity_status="VERIFIED",
        )


def test_authorized_verifier_creates_traceable_verified_measurement():
    engine, authority = _engine_and_verifier()
    candidate = MeasurementEvidence(
        measurement_id="MEAS-1",
        source="sensor",
        description="temperature",
        reference="log-1",
        revision=2,
    )

    verified = engine.verify_evidence(
        candidate,
        authority=authority,
        method="sensor-check-v1",
        criteria="calibration and source identity match",
        reference="CAL-1",
        integrity="HASH-1",
        limitations="single measurement",
        domain="thermal",
    )

    assert verified.evidence_state.value == "VERIFIED"
    assert verified.verification_record_id
    record = engine.get_verification_record(verified.verification_record_id)
    assert record.evidence_id == "MEAS-1"
    assert record.evidence_revision == 2
    assert record.verifier == "VERIFIER-1"
    assert engine.is_verified_by_record(verified)


def test_wrong_scope_cannot_promote_evidence():
    engine, authority = _engine_and_verifier()
    candidate = MeasurementEvidence(
        measurement_id="MEAS-2",
        source="sensor",
        description="temperature",
        reference="log-2",
    )

    with pytest.raises(PermissionError, match="scope"):
        engine.verify_evidence(
            candidate,
            authority=authority,
            method="other-method",
            criteria="criteria",
            reference="REF",
            integrity="HASH",
            limitations="none",
            domain="thermal",
        )


def test_revoked_authority_cannot_promote():
    engine, authority = _engine_and_verifier()
    engine.revoke_authority(authority.grant_id, actor=_grantor())
    candidate = MeasurementEvidence(
        measurement_id="MEAS-3",
        source="sensor",
        description="temperature",
        reference="log-3",
    )

    with pytest.raises(PermissionError, match="expired or revoked"):
        engine.verify_evidence(
            candidate,
            authority=authority,
            method="sensor-check-v1",
            criteria="criteria",
            reference="REF",
            integrity="HASH",
            limitations="none",
            domain="thermal",
        )


def test_revision_is_bound_to_verification_record():
    engine, authority = _engine_and_verifier()
    candidate = MeasurementEvidence(
        measurement_id="MEAS-4",
        source="sensor",
        description="temperature",
        reference="log-4",
        revision=7,
    )
    verified = engine.verify_evidence(
        candidate,
        authority=authority,
        method="sensor-check-v1",
        criteria="criteria",
        reference="REF",
        integrity="HASH",
        limitations="none",
        domain="thermal",
    )
    changed_revision = MeasurementEvidence(
        measurement_id=verified.measurement_id,
        source=verified.source,
        description=verified.description,
        reference=verified.reference,
        evidence_state=verified.evidence_state,
        revision=8,
        verification_record_id=verified.verification_record_id,
    )
    assert not engine.is_verified_by_record(changed_revision)


def test_approval_requires_explicit_approval_authority():
    workflow = ApprovalWorkflow()
    with pytest.raises((TypeError, PermissionError)):
        workflow.approve("proposal", "validator")

    approval_authority = Authority(
        identity="APPROVER-1",
        level=2,
        scope="proposal",
        action="APPROVE",
        grant_id="APPROVAL-GRANT-1",
        grantor="CONSTITUTION",
    )
    result = workflow.approve("proposal", approval_authority)
    assert result["status"] == "APPROVED"
    assert result["approved_by"] == "APPROVER-1"
