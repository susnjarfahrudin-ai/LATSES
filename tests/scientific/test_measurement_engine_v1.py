from __future__ import annotations

import pytest

from lat_ces.core.dimensions import LENGTH, MASS, TIME, Unit
from lat_ces.scientific.quantity import Quantity
from lat_ces.scientific.measurement import (
    CalibrationRecord,
    Instrument,
    Measurement,
    MeasurementAudit,
    MeasurementEvidence,
    MeasurementProvenance,
    MeasurementRegistry,
    Uncertainty,
    create_audit,
    create_revision,
    harden_measurement,
    measurement_hash,
    measurement_to_sko,
    hardened_measurement_to_sko,
    validate_hardened_measurement,
)


METER = Unit("meter", "m", LENGTH)
KILOGRAM = Unit("kilogram", "kg", MASS)
SECOND = Unit("second", "s", TIME)


def make_quantity(value: float = 23.4) -> Quantity:
    return Quantity(value=value, unit=METER)


def make_instrument() -> Instrument:
    return Instrument(
        instrument_id="SENSOR-TEMP-001",
        name="Room Temperature Sensor",
        measurement_range=(-40.0, 125.0),
        accuracy=0.2,
        manufacturer="Test Instruments",
        unit=METER,
        calibration_required=True,
    )


def make_calibration() -> CalibrationRecord:
    return CalibrationRecord(
        calibration_id="CAL-2026-001",
        instrument_id="SENSOR-TEMP-001",
        standard="REF-TEMP-001",
        date="2026-01-15",
        certificate="CERT-2026-001",
    )


def make_provenance() -> MeasurementProvenance:
    return MeasurementProvenance.now(
        source="instrument:SENSOR-TEMP-001",
        recorded_by="LAT-CES-test",
        evidence_id="EVID-001",
    )


def make_measurement() -> Measurement:
    return Measurement(
        quantity=make_quantity(),
        uncertainty=Uncertainty(value=0.2, method="sensor accuracy", confidence=95),
        instrument=make_instrument(),
        calibration=make_calibration(),
        provenance=make_provenance(),
        method="direct sensor observation",
        source="instrument:SENSOR-TEMP-001",
    )


def test_measurement_creation() -> None:
    m = make_measurement()
    assert m.value == pytest.approx(23.4)
    assert m.unit == METER
    assert m.quantity.dimension == LENGTH


def test_measurement_identity_is_generated_and_stable() -> None:
    m = make_measurement()
    assert m.measurement_id.startswith("MEAS-")
    assert m.measurement_id == m.measurement_id


def test_measurement_requires_canonical_quantity() -> None:
    with pytest.raises(TypeError):
        Measurement(quantity=23.4)  # type: ignore[arg-type]


def test_measurement_unit_cannot_conflict_with_quantity() -> None:
    with pytest.raises(ValueError):
        Measurement(
            quantity=make_quantity(),
            unit=KILOGRAM,
            uncertainty=Uncertainty(0.2, "accuracy"),
            instrument=make_instrument(),
            calibration=make_calibration(),
            provenance=make_provenance(),
        )


def test_quantity_reference_validation() -> None:
    m = make_measurement()
    assert m.quantity is not None
    assert m.dimension == LENGTH


def test_dimension_mismatch_is_rejected() -> None:
    pressure_unit = Unit("pascal", "Pa", MASS / (LENGTH * (TIME ** 2)))
    with pytest.raises(ValueError):
        Measurement(
            quantity=make_quantity(),
            unit=pressure_unit,
            uncertainty=Uncertainty(0.2, "accuracy"),
            instrument=make_instrument(),
            calibration=make_calibration(),
            provenance=make_provenance(),
        )


def test_uncertainty_registration() -> None:
    m = make_measurement()
    assert isinstance(m.uncertainty, Uncertainty)
    assert m.uncertainty.value == pytest.approx(0.2)
    assert m.uncertainty.confidence == 95


def test_invalid_uncertainty_is_rejected() -> None:
    with pytest.raises(ValueError):
        Uncertainty(-0.1, "accuracy")


def test_uncertainty_method_trace() -> None:
    u = Uncertainty(0.2, "sensor accuracy", confidence=95)
    assert u.method == "sensor accuracy"
    assert u.confidence == 95


def test_instrument_association() -> None:
    m = make_measurement()
    assert m.instrument.instrument_id == "SENSOR-TEMP-001"


def test_instrument_identity_validation() -> None:
    with pytest.raises(ValueError):
        Instrument("", "sensor", (-1, 1), 0.1)


def test_calibration_record_validation_and_hash() -> None:
    calibration = make_calibration()
    assert calibration.instrument_id == "SENSOR-TEMP-001"
    assert calibration.verify_integrity()


def test_calibration_trace_link() -> None:
    m = make_measurement()
    assert m.calibration.instrument_id == m.instrument.instrument_id


def test_timestamp_requirement() -> None:
    m = make_measurement()
    assert m.timestamp


def test_measurement_registry_storage_and_retrieval() -> None:
    registry = MeasurementRegistry()
    m = make_measurement()
    registry.register(m)
    assert registry.get(m.measurement_id) == m
    assert len(registry) == 1


def test_sko_measurement_registration() -> None:
    m = make_measurement()
    sko = measurement_to_sko(m)
    assert sko.sko_id == f"SKO-{m.measurement_id}"
    assert sko.payload["object_type"] == "Measurement"


def test_complete_hardened_traceability() -> None:
    m = make_measurement()
    evidence = MeasurementEvidence(
        measurement_id=m.measurement_id,
        source="sensor-record",
        description="Original sensor observation",
        reference="sensor/SENSOR-TEMP-001/2026-08-26T00:00:00Z",
    )
    audit = create_audit(m, "CREATE", actor="SYSTEM")
    hardened = harden_measurement(m, audit=audit, evidence=evidence)
    assert validate_hardened_measurement(hardened) is hardened
    sko = hardened_measurement_to_sko(hardened)
    assert sko.payload["integrity_hash"] == hardened.integrity_hash


def test_provenance_can_supply_source_without_duplicate_source_field() -> None:
    m = Measurement(
        quantity=make_quantity(),
        uncertainty=Uncertainty(0.2, "sensor accuracy"),
        instrument=make_instrument(),
        calibration=make_calibration(),
        provenance=make_provenance(),
        method="",
        source="",
    )
    assert m.resolved_source == "instrument:SENSOR-TEMP-001"
    assert m.validate() is m


def test_measurement_revision_preserves_identity() -> None:
    original = make_measurement()
    changed = original.revise(
        reason="Corrected sensor reading",
        quantity=make_quantity(24.1),
    )
    assert changed.measurement_id == original.measurement_id
    assert changed.revision == original.revision + 1
    previous_hash = measurement_hash(original)
    new_hash = measurement_hash(changed)
    revision = create_revision(
        original,
        changed,
        previous_hash=previous_hash,
        new_hash=new_hash,
        reason="Corrected sensor reading",
    )
    assert revision.previous_hash == previous_hash
    assert revision.new_hash == new_hash
    assert revision.revision == "B"


def test_measurement_hash_is_deterministic() -> None:
    m = make_measurement()
    assert measurement_hash(m) == measurement_hash(m)


def test_value_change_is_detected_by_hash() -> None:
    original = make_measurement()
    changed = original.revise(reason="corrected", quantity=make_quantity(25.4))
    assert measurement_hash(original) != measurement_hash(changed)


def test_hardened_measurement_requires_matching_evidence() -> None:
    m = make_measurement()
    other = make_measurement()
    evidence = MeasurementEvidence(other.measurement_id, "sensor", "record", "ref")
    audit = create_audit(m, "CREATE")
    with pytest.raises(ValueError):
        harden_measurement(m, audit=audit, evidence=evidence)


def test_hardened_measurement_rejects_tampered_hash() -> None:
    m = make_measurement()
    evidence = MeasurementEvidence(m.measurement_id, "sensor", "record", "ref")
    audit = create_audit(m, "CREATE")
    hardened = harden_measurement(m, audit=audit, evidence=evidence)
    tampered = type(hardened)(m, "0" * 64, hardened.revision, hardened.audit, hardened.evidence)
    with pytest.raises(ValueError):
        validate_hardened_measurement(tampered)


def test_calibration_modification_is_detected() -> None:
    calibration = make_calibration()
    altered = CalibrationRecord(
        calibration_id=calibration.calibration_id,
        instrument_id=calibration.instrument_id,
        standard=calibration.standard,
        date=calibration.date,
        certificate="CERT-ALTERED",
        integrity_hash=calibration.integrity_hash,
    )
    assert not altered.verify_integrity()


def test_audit_record_carries_measurement_identity_and_revision() -> None:
    m = make_measurement()
    audit = create_audit(m, "CREATE", actor="SYSTEM")
    assert isinstance(audit, MeasurementAudit)
    assert audit.measurement_id == m.measurement_id
    assert audit.revision == "A"


def test_legacy_device_facade_remains_available() -> None:
    from lat_ces.scientific.measurement.compatibility import MeasurementDevice, AccuracySpec
    device = MeasurementDevice("Legacy", "sensor", METER, AccuracySpec(0.0, 0.1), 0.0, 100.0)
    reading = device.measure(10.0)
    assert reading.value == pytest.approx(10.0)
