from __future__ import annotations

from .measurement import Measurement


class MeasurementValidationError(ValueError):
    """Raised when a Measurement violates the SCI measurement contract."""


def validate_measurement(measurement: Measurement) -> Measurement:
    if measurement.quantity is None:
        raise MeasurementValidationError("MEAS-001: measurement requires a physical quantity")
    if measurement.unit is None:
        raise MeasurementValidationError("MEAS-002: measurement requires a unit")
    if getattr(measurement.unit, "dimension", None) is None:
        raise MeasurementValidationError("MEAS-002: unit requires a dimension")
    quantity_dimension = getattr(measurement.quantity, "dimension", None)
    if quantity_dimension is not None and quantity_dimension != measurement.unit.dimension:
        raise MeasurementValidationError("MEAS-002: unit dimension does not match quantity dimension")
    if measurement.instrument is None:
        raise MeasurementValidationError("MEAS-003: measurement requires a known instrument")
    if measurement.uncertainty is None:
        raise MeasurementValidationError("MEAS-004: measurement uncertainty must be recorded")
    if measurement.uncertainty < 0:
        raise MeasurementValidationError("MEAS-004: measurement uncertainty cannot be negative")
    if not measurement.timestamp:
        raise MeasurementValidationError("MEAS-005: measurement requires a timestamp")
    if measurement.provenance is None:
        raise MeasurementValidationError("Measurement requires provenance")
    return measurement
