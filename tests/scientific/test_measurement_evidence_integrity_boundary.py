from lat_ces.scientific.evidence_state import EvidenceState
from lat_ces.scientific.measurement import MeasurementEvidence, harden_measurement
from tests.scientific.test_measurement_contract import valid_measurement


def test_integrity_must_bind_measurement_evidence_state():
    measurement = valid_measurement()
    unknown = MeasurementEvidence(
        measurement_id=measurement.measurement_id,
        source="sensor-log",
        description="temperature reading",
        reference="log-1",
        evidence_state=EvidenceState.UNKNOWN,
    )
    verified = MeasurementEvidence(
        measurement_id=measurement.measurement_id,
        source="sensor-log",
        description="temperature reading",
        reference="log-1",
        evidence_state=EvidenceState.VERIFIED,
    )

    unknown_hardened = harden_measurement(measurement, audit=object(), evidence=unknown)
    verified_hardened = harden_measurement(measurement, audit=object(), evidence=verified)

    assert unknown_hardened.evidence.evidence_state is EvidenceState.UNKNOWN
    assert verified_hardened.evidence.evidence_state is EvidenceState.VERIFIED
    assert unknown_hardened.integrity_hash != verified_hardened.integrity_hash
