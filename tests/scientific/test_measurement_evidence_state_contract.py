import pytest

from lat_ces.scientific.evidence_state import EvidenceState
from lat_ces.scientific.measurement.evidence import MeasurementEvidence


def test_measurement_evidence_defaults_to_unknown():
    evidence = MeasurementEvidence(
        measurement_id="MEAS-1",
        source="sensor",
        description="temperature reading",
        reference="sensor-log-1",
    )

    assert evidence.evidence_state is EvidenceState.UNKNOWN
    assert evidence.to_record()["evidence_state"] == "UNKNOWN"


def test_measurement_evidence_cannot_self_declare_verified():
    with pytest.raises(ValueError, match="verification record"):
        MeasurementEvidence(
            measurement_id="MEAS-1",
            source="sensor",
            description="temperature reading",
            reference="sensor-log-1",
            evidence_state=EvidenceState.VERIFIED,
        )
