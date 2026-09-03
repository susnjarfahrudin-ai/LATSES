"""Canonical Measurement contract tests."""

from datetime import datetime, timezone

import pytest

from lat_ces.scientific.measurement.measurement import (
    Measurement,
    MeasurementError,
    MeasurementValidationError,
)
from lat_ces.scientific.measurement.provenance import MeasurementProvenance
from lat_ces.scientific.measurement.uncertainty import Uncertainty
from lat_ces.scientific.quantity import Quantity
from lat_ces.scientific.units.units import celsius, meter
from lat_ces.scientific.core.dimensions import TEMPERATURE


def valid_instrument():
    return "SENSOR-TEMP-001"


def valid_measurement():
    return Measurement(
        quantity=Quantity(TEMPERATURE),
        value=23.4,
        unit=celsius,
        uncertainty=Uncertainty(0.2, "sensor accuracy"),
        instrument=valid_instrument(),
        calibration="CAL-2026-01",
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
        building_model_id="BUILDING-001",
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
        building_model_id="BUILDING-001",
    )
    with pytest.raises(MeasurementValidationError):
        measurement.validate()


