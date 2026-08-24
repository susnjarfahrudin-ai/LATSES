import pytest

from lat_ces.scientific.dimensions.dimension import LENGTH, TEMPERATURE
from lat_ces.scientific.measurement import (
    Measurement,
    MeasurementProvenance,
    MeasurementRegistry,
    MeasurementValidationError,
)
from lat_ces.scientific.units.core import meter, celsius


class Quantity:
    def __init__(self, dimension):
        self.dimension = dimension


def valid_measurement():
    return Measurement(
        quantity=Quantity(TEMPERATURE),
        value=23.4,
        unit=celsius,
        uncertainty=0.2,
        instrument="SENSOR-TEMP-001",
        calibration="CAL-2026-01",
        provenance=MeasurementProvenance.now(
            source="instrument:SENSOR-TEMP-001",
            recorded_by="LAT-CES-test",
            evidence_id="EVID-001",
        ),
    )


def test_measurement_has_persistent_identity_and_validates():
    measurement = valid_measurement()
    assert measurement.measurement_id.startswith("MEAS-")
    assert measurement.validate() is measurement


def test_measurement_rejects_missing_uncertainty():
    measurement = Measurement(
        quantity=Quantity(TEMPERATURE),
        value=23.4,
        unit=celsius,
        uncertainty=None,
        instrument="SENSOR-TEMP-001",
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
        uncertainty=0.2,
        instrument="SENSOR-TEMP-001",
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
