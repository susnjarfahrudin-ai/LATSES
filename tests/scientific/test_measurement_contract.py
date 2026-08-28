import pytest

from lat_ces.scientific.dimensions.dimension import LENGTH, TEMPERATURE
from lat_ces.scientific.measurement import (
    CalibrationRecord,
    Instrument,
    Measurement,
    MeasurementProvenance,
    MeasurementRegistry,
    MeasurementValidationError,
    Uncertainty,
)
from lat_ces.scientific.units.core import meter, celsius


class Quantity:
    """Minimal structural quantity contract used by the SCI validation test."""

    def __init__(self, dimension):
        self.dimension = dimension


def valid_instrument():
    return Instrument(
        instrument_id="SENSOR-TEMP-001",
        name="Room Temperature Sensor",
        measurement_range=(-40.0, 125.0),
        accuracy=0.2,
        unit=celsius,
        calibration_required=False,
    )


def valid_calibration():
    return CalibrationRecord(
        calibration_id="CAL-2026-01",
        instrument_id="SENSOR-TEMP-001",
        standard="REF-TEMP-001",
        date="2026-01-15",
        certificate="CERT-2026-001",
    )


def valid_measurement():
    return Measurement(
        quantity=Quantity(TEMPERATURE),
        value=23.4,
        unit=celsius,
        uncertainty=Uncertainty(0.2, "sensor accuracy", confidence=95),
        instrument=valid_instrument(),
        calibration=valid_calibration(),
        provenance=MeasurementProvenance.now(
            source="instrument:SENSOR-TEMP-001",
            recorded_by="LAT-CES-test",
            evidence_id="EVID-001",
        ),
        building_model_id="BUILDING-001",
        location="room:living",
    )


def test_measurement_has_persistent_identity_and_validates():
    measurement = valid_measurement()
    assert measurement.measurement_id.startswith("MEAS-")
    assert measurement.building_model_id == "BUILDING-001"
    assert measurement.location == "room:living"
    assert measurement.validate() is measurement


def test_measurement_record_contains_canonical_model_binding():
    record = valid_measurement().to_record()
    assert record["building_model_id"] == "BUILDING-001"
    assert record["location"] == "room:living"


def test_measurement_rejects_missing_building_model_identity():
    measurement = Measurement(
        quantity=Quantity(TEMPERATURE),
        value=23.4,
        unit=celsius,
        uncertainty=0.2,
        instrument="SENSOR-TEMP-001",
        provenance=MeasurementProvenance.now(
            source="instrument:SENSOR-TEMP-001", recorded_by="LAT-CES-test"
        ),
    )
    with pytest.raises(MeasurementValidationError, match="MEAS-000"):
        measurement.validate()


def test_measurement_rejects_missing_uncertainty():
    measurement = Measurement(
        quantity=Quantity(TEMPERATURE),
        value=23.4,
        unit=celsius,
        uncertainty=None,
        instrument=valid_instrument(),
        provenance=MeasurementProvenance.now(
            source="instrument:SENSOR-TEMP-001", recorded_by="LAT-CES-test"
        ),
    )
    with pytest.raises(MeasurementValidationError, match="MEAS-004"):
        measurement.validate()


def test_measurement_rejects_dimension_mismatch():
    measurement = Measurement(
        quantity=Quantity(TEMPERATURE),
        value=23.4,
        unit=meter,
        uncertainty=Uncertainty(0.2, "sensor accuracy"),
        instrument=valid_instrument(),
        provenance=MeasurementProvenance.now(
            source="instrument:SENSOR-TEMP-001", recorded_by="LAT-CES-test"
        ),
    )
    with pytest.raises(MeasurementValidationError, match="MEAS-002"):
        measurement.validate()


def test_registry_requires_valid_measurements_and_preserves_identity():
    registry = MeasurementRegistry()
    measurement = valid_measurement()
    registry.register(measurement)
    assert len(registry) == 1
    assert registry.get(measurement.measurement_id) is measurement
