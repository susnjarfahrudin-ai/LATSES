import math

import pytest

from lat_ces.core.dimensions import LENGTH, Unit
from lat_ces.scientific.measurement import (
    AccuracySpec,
    Measurement,
    MeasurementDevice,
    MeasurementError,
    OutOfRangeError,
    create_diff_pressure_sensor,
    create_pitot_tube,
)
from lat_ces.scientific.quantity import Quantity


def test_measurement_device_applies_calibration_and_uncertainty():
    meter = Unit("meter", "m", LENGTH)
    device = MeasurementDevice(
        name="laser rangefinder",
        device_type="distance",
        unit=meter,
        accuracy_spec=AccuracySpec(relative_error=0.01, absolute_error=0.05),
        min_range=0.0,
        max_range=200.0,
        calibration_offset=0.5,
        sko_uuid="device-123",
    )

    measurement = device.measure(100.0)

    assert measurement.value == 99.5
    assert math.isclose(measurement.uncertainty, 1.045)
    assert measurement.unit is meter
    assert measurement._uuid == "device-123"


def test_measurement_now_creates_contextual_canonical_record():
    meter = Unit("meter", "m", LENGTH)
    quantity = Quantity(21.0, meter, provenance="room-r01")

    measurement = Measurement.now(
        quantity,
        method="calibrated_laser",
        source="instrument:LASER-01",
        instrument_id="LASER-01",
        location="Room-R01",
        subject="wall-W01",
        calibration_reference="CAL-2026-01",
        operator="engineer-01",
        uncertainty_ref="UNC-01",
    )

    assert measurement.measurement_id.startswith("LAT-MEAS-")
    assert measurement.value == pytest.approx(21.0)
    assert measurement.unit is meter
    assert measurement.dimension == LENGTH
    assert measurement.provenance == "room-r01"
    assert measurement.instrument_id == "LASER-01"
    assert measurement.calibration_reference == "CAL-2026-01"
    assert measurement.uncertainty_ref == "UNC-01"


def test_measurement_requires_context_and_quantity():
    meter = Unit("meter", "m", LENGTH)
    quantity = Quantity(1.0, meter)

    with pytest.raises(MeasurementError):
        Measurement(quantity, "", "manual", "field")
    with pytest.raises(MeasurementError):
        Measurement(quantity, "2026-08-26T00:00:00+00:00", "", "field")
    with pytest.raises(TypeError):
        Measurement("not-a-quantity", "2026-08-26T00:00:00+00:00", "manual", "field")


def test_measurement_device_accepts_range_boundaries():
    meter = Unit("meter", "m", LENGTH)
    device = MeasurementDevice("meter", "distance", meter, AccuracySpec(), 1.0, 2.0)

    assert device.measure(1.0).value == 1.0
    assert device.measure(2.0).value == 2.0


def test_measurement_device_rejects_out_of_range_values():
    meter = Unit("meter", "m", LENGTH)
    device = MeasurementDevice("meter", "distance", meter, AccuracySpec(), 1.0, 2.0)

    with pytest.raises(OutOfRangeError):
        device.measure(0.99)
    with pytest.raises(OutOfRangeError):
        device.measure(2.01)


def test_measurement_configuration_rejects_invalid_errors_and_range():
    meter = Unit("meter", "m", LENGTH)

    with pytest.raises(ValueError):
        AccuracySpec(relative_error=-0.01)
    with pytest.raises(ValueError):
        AccuracySpec(absolute_error=-0.01)
    with pytest.raises(ValueError):
        MeasurementDevice("meter", "distance", meter, AccuracySpec(), 2.0, 2.0)


def test_create_pitot_tube_factory():
    pitot = create_pitot_tube("Roof Pitot")

    assert pitot.name == "Roof Pitot"
    assert pitot.device_type == "Pitot Tube"
    assert pitot.unit.symbol == "m/s"
    assert pitot.min_range == 1.0
    assert pitot.max_range == 40.0
    assert pitot.accuracy_spec.relative_error == 0.015
    assert pitot.accuracy_spec.absolute_error == 0.1


def test_create_diff_pressure_sensor_factory():
    sensor = create_diff_pressure_sensor()

    assert sensor.name == "Plenum DP Sensor"
    assert sensor.device_type == "Differential Pressure Transmitter"
    assert sensor.unit.symbol == "Pa"
    assert sensor.min_range == 0.0
    assert sensor.max_range == 2000.0
    assert sensor.accuracy_spec.relative_error == 0.005
    assert sensor.accuracy_spec.absolute_error == 1.0
