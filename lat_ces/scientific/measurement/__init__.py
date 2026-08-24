"""Canonical SCI-0046/0047 measurement contract and legacy exports."""
"""Canonical SCI-0046/0047 measurement contract and compatibility facade."""

from .measurement import Measurement
from .provenance import MeasurementProvenance
from .validation import MeasurementValidationError, validate_measurement
from .registry import MeasurementRegistry
from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.scientific.measurement_legacy import (
from .compatibility import (
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
    "PhysicalQuantity",
    "AccuracySpec",
    "MeasurementDevice",
    "OutOfRangeError",
    "create_pitot_tube",
    "create_diff_pressure_sensor",
]
