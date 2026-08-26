"""Canonical SCI-0046/0047 measurement contract and compatibility facade."""

from .measurement import Measurement, MeasurementError
from .provenance import MeasurementProvenance
from .validation import MeasurementValidationError, validate_measurement
from .registry import MeasurementRegistry
from lat_ces.scientific.quantity import PhysicalQuantity
from .compatibility import (
    AccuracySpec,
    MeasurementDevice,
    OutOfRangeError,
    create_diff_pressure_sensor,
    create_pitot_tube,
)

__all__ = [
    "Measurement",
    "MeasurementError",
    "MeasurementProvenance",
    "MeasurementValidationError",
    "validate_measurement",
    "MeasurementRegistry",
    "PhysicalQuantity",
    "AccuracySpec",
    "MeasurementDevice",
    "OutOfRangeError",
    "create_pitot_tube",
    "create_diff_pressure_sensor",
]
