"""Canonical SCI measurement engine and compatibility exports."""

from .measurement import Measurement, MeasurementError
from .instrument import Instrument, InstrumentValidationError
from .calibration import CalibrationRecord, CalibrationValidationError
from .uncertainty import Uncertainty, UncertaintyValidationError
from .provenance import MeasurementProvenance
from .evidence import MeasurementEvidence
from .revision import MeasurementRevision, create_revision, revision_label
from .audit import MeasurementAudit, create_audit
from .integrity import HardenedMeasurement, harden_measurement, measurement_hash, verify_integrity
from .validation import MeasurementValidationError, validate_measurement, validate_hardened_measurement
from .registry import MeasurementRegistry
from .sko_integration import measurement_to_sko, hardened_measurement_to_sko
from .compatibility import (
    AccuracySpec,
    MeasurementDevice,
    OutOfRangeError,
    create_diff_pressure_sensor,
    create_pitot_tube,
)
from lat_ces.scientific.quantity import PhysicalQuantity, Quantity, QuantityError

__all__ = [
    "Measurement",
    "MeasurementError",
    "Instrument",
    "InstrumentValidationError",
    "CalibrationRecord",
    "CalibrationValidationError",
    "Uncertainty",
    "UncertaintyValidationError",
    "MeasurementProvenance",
    "MeasurementEvidence",
    "MeasurementRevision",
    "create_revision",
    "revision_label",
    "MeasurementAudit",
    "create_audit",
    "HardenedMeasurement",
    "harden_measurement",
    "measurement_hash",
    "verify_integrity",
    "MeasurementValidationError",
    "validate_measurement",
    "validate_hardened_measurement",
    "MeasurementRegistry",
    "measurement_to_sko",
    "hardened_measurement_to_sko",
    "PhysicalQuantity",
    "Quantity",
    "QuantityError",
    "AccuracySpec",
    "MeasurementDevice",
    "OutOfRangeError",
    "create_diff_pressure_sensor",
    "create_pitot_tube",
]
