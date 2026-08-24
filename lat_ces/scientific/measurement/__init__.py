"""Canonical SCI-0046/0047 measurement contract and compatibility exports."""

from .measurement import Measurement
from .provenance import MeasurementProvenance
from .validation import MeasurementValidationError, validate_measurement
from .registry import MeasurementRegistry
from .legacy_device import (
    AccuracySpec,
    MeasurementDevice,
    OutOfRangeError,
    create_diff_pressure_sensor,
    create_pitot_tube,
)

__all__ = [
    "Measurement",
    "MeasurementProvenance",
    "MeasurementValidationError",
    "validate_measurement",
    "MeasurementRegistry",
    "AccuracySpec",
    "MeasurementDevice",
    "OutOfRangeError",
    "create_diff_pressure_sensor",
    "create_pitot_tube",
]
