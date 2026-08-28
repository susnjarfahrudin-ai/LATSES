from __future__ import annotations

from .measurement import Measurement, MeasurementError


class MeasurementValidationError(MeasurementError):
    """Raised when a Measurement violates the SCI-CORE-0046 contract."""


def validate_measurement(measurement: Measurement) -> Measurement:
    if not isinstance(measurement, Measurement):
        raise MeasurementValidationError("expected Measurement")
    if measurement.quantity is None:
        raise MeasurementValidationError("MEAS-001: measurement requires a physical quantity")
    if measurement.unit is None:
        raise MeasurementValidationError("MEAS-002: measurement requires a unit")
    if getattr(measurement.unit, "dimension", None) is None:
        raise MeasurementValidationError("MEAS-002: unit requires a dimension")
    if measurement.quantity.dimension != measurement.unit.dimension:
        raise MeasurementValidationError("MEAS-002: unit dimension does not match quantity dimension")
    if measurement.instrument is None:
        raise MeasurementValidationError("MEAS-003: measurement requires a known instrument")
    instrument_id = getattr(measurement.instrument, "instrument_id", None) or getattr(measurement.instrument, "uuid", None)
    if not instrument_id:
        raise MeasurementValidationError("MEAS-003: instrument requires a stable identity")
    if hasattr(measurement.instrument, "validate_value"):
        measurement.instrument.validate_value(measurement.value)
    if measurement.uncertainty is None:
        raise MeasurementValidationError("MEAS-004: measurement uncertainty must be recorded")
    uncertainty_value = getattr(measurement.uncertainty, "value", measurement.uncertainty)
    if uncertainty_value < 0:
        raise MeasurementValidationError("MEAS-004: measurement uncertainty cannot be negative")
    if not measurement.timestamp:
        raise MeasurementValidationError("MEAS-005: measurement requires a timestamp")
    if measurement.provenance is None:
        raise MeasurementValidationError("MEAS-006: measurement requires provenance")
    if not measurement.source:
        raise MeasurementValidationError("MEAS-007: measurement requires a source")
    calibration_required = getattr(measurement.instrument, "calibration_required", False)
    if calibration_required and measurement.calibration is None:
        raise MeasurementValidationError("MEAS-008: calibrated instrument requires a calibration record")
    if measurement.calibration is not None:
        if getattr(measurement.calibration, "instrument_id", None) != instrument_id:
            raise MeasurementValidationError("MEAS-009: calibration instrument does not match measurement instrument")
        if hasattr(measurement.calibration, "verify_integrity") and not measurement.calibration.verify_integrity():
            raise MeasurementValidationError("MEAS-010: calibration integrity verification failed")
    return measurement


def validate_hardened_measurement(hardened) -> object:
    validate_measurement(hardened.measurement)
    if not hardened.integrity_hash:
        raise MeasurementValidationError("Missing integrity hash")
    if not hardened.audit:
        raise MeasurementValidationError("Missing audit")
    if not hardened.evidence:
        raise MeasurementValidationError("Missing evidence")
    from .integrity import verify_integrity
    if not verify_integrity(hardened.measurement, hardened.integrity_hash):
        raise MeasurementValidationError("Integrity verification failed")
    if hardened.evidence.measurement_id != hardened.measurement.measurement_id:
        raise MeasurementValidationError("Evidence measurement_id does not match measurement")
    if hardened.audit.measurement_id != hardened.measurement.measurement_id:
        raise MeasurementValidationError("Audit measurement_id does not match measurement")
    return hardened


__all__ = ["MeasurementValidationError", "validate_measurement", "validate_hardened_measurement"]
