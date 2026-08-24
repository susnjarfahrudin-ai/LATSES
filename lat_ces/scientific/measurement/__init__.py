"""Canonical SCI-0046/0047 measurement contract and compatibility exports."""
"""Canonical SCI-0046/0047 measurement contract and compatibility facade."""

from .measurement import Measurement
from .provenance import MeasurementProvenance
from .validation import MeasurementValidationError, validate_measurement
from .registry import MeasurementRegistry
from .legacy_device import (
from lat_ces.scientific.quantity import PhysicalQuantity
from .compatibility import (
    AccuracySpec,
    MeasurementDevice,
    OutOfRangeError,
    create_diff_pressure_sensor,
    create_pitot_tube,
)
# Historical callers exposed PhysicalQuantity from ``scientific.measurement``.
# Keep that import path as a compatibility facade while the canonical
# implementation remains in ``scientific.quantity``.
from lat_ces.scientific.quantity import PhysicalQuantity

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
    "PhysicalQuantity",
    "PhysicalQuantity",
    "AccuracySpec",
    "MeasurementDevice",
    "OutOfRangeError",
    "create_pitot_tube",
    "create_diff_pressure_sensor",
]
