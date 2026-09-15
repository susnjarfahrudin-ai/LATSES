import pytest

from lat_ces.scientific.core.knowledge_validation_sci0062_0145 import ScientificEvidence
from lat_ces.scientific.governance.approval import ApprovalWorkflow
from lat_ces.scientific.governance.authority import Authority
from lat_ces.scientific.governance.governance_engine import ScientificKnowledgeGovernanceEngine
from lat_ces.scientific.measurement.evidence import MeasurementEvidence


def _grantor(engine: ScientificKnowledgeGovernanceEngine) -> Authority:
    return engine.canonical_root_authority


def _engine_and_verifier() -> tuple[ScientificKnowledgeGovernanceEngine, Authority]:
    engine = ScientificKnowledgeGovernanceEngine()
    verifier = engine.grant_verification_authority(
        grantor=_grantor(engine),
        verifier_identity="VERIFIER-1",
        scope="measurement",
        evidence_type="MeasurementEvidence",
        domain="thermal",
        method="sensor-check-v1",
    )
    return engine, verifier


def _candidate(measurement_id: str = "MEAS-1", revision: int = 2) -> MeasurementEvidence:
    return MeasurementEvidence(
        measurement_id=measurement_id,
        source="sensor",
        description="temperature",
        reference="log-1",
        revision=revision,
    )


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


def test_verified_without_verification_record_must_fail():
    with pytest.raises(ValueError, match="verification record"):
        MeasurementEvidence(
            measurement_id="MEAS-0",
            source="sensor",
            description="temperature",
            reference="log-0",
            evidence_state="VERIFIED",
        )


def test_authorized_verifier_creates_traceable_verified_measurement():
    engine, authority = _engine_and_verifier()
    verified = engine.verify_evidence(
        _candidate(),
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


def test_nonexistent_verification_record_must_not_validate():
    engine, _ = _engine_and_verifier()
    forged = MeasurementEvidence(
        measurement_id="MEAS-2",
        source="sensor",
        description="temperature",
        reference="log-2",
        evidence_state="VERIFIED",
        revision=1,
        verification_record_id="VER-DOES-NOT-EXIST",
    )

    assert not engine.is_verified_by_record(forged)


def test_verification_record_wrong_measurement_id_must_not_validate():
    engine, authority = _engine_and_verifier()
    verified = engine.verify_evidence(
        _candidate("MEAS-3", 4),
        authority=authority,
        method="sensor-check-v1",
        criteria="criteria",
        reference="REF",
        integrity="HASH",
        limitations="none",
        domain="thermal",
    )
    wrong_measurement = MeasurementEvidence(
        measurement_id="MEAS-WRONG",
        source=verified.source,
        description=verified.description,
        reference=verified.reference,
        evidence_state=verified.evidence_state,
        revision=verified.revision,
        verification_record_id=verified.verification_record_id,
    )

    assert not engine.is_verified_by_record(wrong_measurement)


def test_verification_record_wrong_revision_must_not_validate():
    engine, authority = _engine_and_verifier()
    verified = engine.verify_evidence(
        _candidate("MEAS-4", 7),
        authority=authority,
        method="sensor-check-v1",
        criteria="criteria",
        reference="REF",
        integrity="HASH",
        limitations="none",
        domain="thermal",
    )
    wrong_revision = MeasurementEvidence(
        measurement_id=verified.measurement_id,
        source=verified.source,
        description=verified.description,
        reference=verified.reference,
        evidence_state=verified.evidence_state,
        revision=8,
        verification_record_id=verified.verification_record_id,
    )

    assert not engine.is_verified_by_record(wrong_revision)


def test_unauthorized_verifier_must_fail():
    engine, authority = _engine_and_verifier()
    unauthorized = Authority(
        identity="UNAUTHORIZED",
        level=authority.level,
        scope=authority.scope,
        action=authority.action,
        grant_id=authority.grant_id,
        grantor=authority.grantor,
        parent_grant_id=authority.parent_grant_id,
    )

    with pytest.raises(PermissionError, match="registered grant"):
        engine.verify_evidence(
            _candidate("MEAS-5"),
            authority=unauthorized,
            method="sensor-check-v1",
            criteria="criteria",
            reference="REF",
            integrity="HASH",
            limitations="none",
            domain="thermal",
        )


def test_wrong_scope_cannot_promote_evidence():
    engine, authority = _engine_and_verifier()
    with pytest.raises(PermissionError, match="scope"):
        engine.verify_evidence(
            _candidate("MEAS-6"),
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
    engine.revoke_authority(authority.grant_id, actor=_grantor(engine))

    assert engine.authority_registry.get(authority.grant_id) is authority
    assert engine.authority_registry.is_revoked(authority.grant_id)

    with pytest.raises(PermissionError, match="expired or revoked"):
        engine.verify_evidence(
            _candidate("MEAS-7"),
            authority=authority,
            method="sensor-check-v1",
            criteria="criteria",
            reference="REF",
            integrity="HASH",
            limitations="none",
            domain="thermal",
        )


def test_expired_registered_authority_cannot_promote():
    engine = ScientificKnowledgeGovernanceEngine()
    authority = engine.grant_verification_authority(
        grantor=_grantor(engine),
        verifier_identity="VERIFIER-EXPIRED",
        scope="measurement",
        evidence_type="MeasurementEvidence",
        domain="thermal",
        method="sensor-check-v1",
        valid_until="2000-01-01T00:00:00+00:00",
    )

    assert engine.authority_registry.get(authority.grant_id) is authority

    with pytest.raises(PermissionError, match="expired or revoked"):
        engine.verify_evidence(
            _candidate("MEAS-8"),
            authority=authority,
            method="sensor-check-v1",
            criteria="criteria",
            reference="REF",
            integrity="HASH",
            limitations="none",
            domain="thermal",
        )


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
