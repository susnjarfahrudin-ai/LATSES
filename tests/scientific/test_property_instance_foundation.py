import pytest

from lat_ces.scientific.evidence.property_instance import PropertyInstance
from lat_ces.scientific.evidence_state import EvidenceState


def _property(**overrides: object) -> PropertyInstance:
    values = {
        "property_id": "thermal_conductivity",
        "subject_id": "MATERIAL-001",
        "value": 0.035,
        "unit": "W/(m*K)",
        "source": "manufacturer-declaration",
        "provenance": "DOC-001",
        "evidence_id": "EVID-001",
    }
    values.update(overrides)
    return PropertyInstance(**values)


def test_property_instance_is_immutable_and_identity_bearing():
    instance = _property()

    assert instance.property_id == "thermal_conductivity"
    assert instance.subject_id == "MATERIAL-001"
    assert instance.evidence_state is EvidenceState.UNKNOWN

    with pytest.raises(AttributeError):
        instance.value = 0.04


def test_property_instance_requires_property_identity():
    with pytest.raises(ValueError, match="property_id"):
        _property(property_id="")


def test_property_instance_requires_subject_identity():
    with pytest.raises(ValueError, match="subject_id"):
        _property(subject_id="")


def test_property_instance_requires_unit():
    with pytest.raises(ValueError, match="unit"):
        _property(unit="")


def test_property_instance_requires_evidence_identity():
    with pytest.raises(ValueError, match="evidence_id"):
        _property(evidence_id="")


def test_property_instance_rejects_invalid_revision():
    with pytest.raises(ValueError, match="revision"):
        _property(revision=0)


def test_verified_property_cannot_self_assert_without_verification_record():
    with pytest.raises(ValueError, match="verification record"):
        _property(evidence_state=EvidenceState.VERIFIED)


def test_verified_property_requires_explicit_verification_record_reference():
    instance = _property(
        evidence_state=EvidenceState.VERIFIED,
        verification_record_id="VER-001",
    )

    assert instance.verification_record_id == "VER-001"
    assert instance.evidence_state is EvidenceState.VERIFIED


def test_property_instance_does_not_expose_computational_authority():
    instance = _property()
    record = instance.to_record()

    assert "authority_class" not in record
    assert "accepted_for_calculation" not in record
    assert "cap" not in record
    assert "admission" not in record
