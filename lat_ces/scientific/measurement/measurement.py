from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from numbers import Real
from uuid import uuid4


class MeasurementError(ValueError):
    """Base error for invalid canonical Measurement records."""


@dataclass(frozen=True, init=False)
class Measurement:
    """SCI-0046/0047 canonical contextual measurement record."""

    quantity: object
    timestamp: str
    method: str
    source: str
    instrument_id: str | None
    location: str | None
    subject: str | None
    calibration_reference: str | None
    operator: str | None
    uncertainty_ref: str | None
    value: Real
    unit: object
    uncertainty: float | None
    provenance: object | None
    evidence: object | None
    measurement_id: str
    revision: int

    def __init__(
        self,
        quantity=None,
        timestamp: str | None = None,
        method: str = "",
        source: str = "",
        *,
        value: Real | None = None,
        unit=None,
        uncertainty: float | None = None,
        instrument=None,
        calibration=None,
        instrument_id: str | None = None,
        location: str | None = None,
        subject: str | None = None,
        calibration_reference: str | None = None,
        operator: str | None = None,
        uncertainty_ref: str | None = None,
        provenance=None,
        evidence=None,
        measurement_id: str | None = None,
        revision: int = 1,
    ) -> None:
        if quantity is None and (value is None or unit is None):
            raise TypeError("Measurement requires Quantity or explicit value and unit")
        if quantity is not None and not hasattr(quantity, "dimension") and not hasattr(quantity, "value"):
            raise TypeError("Measurement requires a Quantity-like scientific object")
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()
        if not isinstance(timestamp, str) or not timestamp.strip():
            raise MeasurementError("Measurement timestamp must be a non-empty string")
        if not method:
            method = "unspecified"
        if not source:
            source = "unspecified"
        if uncertainty is not None and float(uncertainty) < 0:
            raise MeasurementError("Measurement uncertainty cannot be negative")
        if revision < 1:
            raise MeasurementError("Measurement revision must be >= 1")

        resolved_instrument = instrument_id if instrument_id is not None else instrument
        resolved_calibration = calibration_reference if calibration_reference is not None else calibration

        if value is None:
            value = getattr(quantity, "value", None)
        if unit is None:
            unit = getattr(quantity, "unit", None)
        if value is None or unit is None:
            raise MeasurementError("Measurement requires a resolvable value and unit")

        quantity_uncertainty = getattr(quantity, "uncertainty", None)
        quantity_provenance = getattr(quantity, "provenance", None)

        object.__setattr__(self, "quantity", quantity)
        object.__setattr__(self, "timestamp", timestamp)
        object.__setattr__(self, "method", method)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "instrument_id", resolved_instrument)
        object.__setattr__(self, "location", location)
        object.__setattr__(self, "subject", subject)
        object.__setattr__(self, "calibration_reference", resolved_calibration)
        object.__setattr__(self, "operator", operator)
        object.__setattr__(self, "uncertainty_ref", uncertainty_ref)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "unit", unit)
        object.__setattr__(self, "uncertainty", float(uncertainty) if uncertainty is not None else quantity_uncertainty)
        object.__setattr__(self, "provenance", provenance if provenance is not None else quantity_provenance)
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(self, "measurement_id", measurement_id or f"MEAS-{uuid4().hex.upper()}")
        object.__setattr__(self, "revision", revision)

    @classmethod
    def now(
        cls,
        quantity,
        *,
        method: str,
        source: str,
        instrument_id: str | None = None,
        location: str | None = None,
        subject: str | None = None,
        calibration_reference: str | None = None,
        operator: str | None = None,
        uncertainty_ref: str | None = None,
        evidence=None,
    ) -> "Measurement":
        """Create a timestamped contextual measurement from a Quantity."""
        return cls(
            quantity,
            datetime.now(timezone.utc).isoformat(),
            method,
            source,
            instrument_id=instrument_id,
            location=location,
            subject=subject,
            calibration_reference=calibration_reference,
            operator=operator,
            uncertainty_ref=uncertainty_ref,
            evidence=evidence,
            measurement_id=f"LAT-MEAS-{uuid4().hex.upper()}",
        )

    @property
    def instrument(self):
        return self.instrument_id

    @property
    def calibration(self):
        return self.calibration_reference

    @property
    def dimension(self):
        return self.unit.dimension

    def validate(self) -> "Measurement":
        from .validation import validate_measurement
        return validate_measurement(self)

    def to_record(self) -> dict[str, object]:
        return {
            "measurement_id": self.measurement_id,
            "quantity": self.quantity,
            "value": self.value,
            "unit": self.unit,
            "uncertainty": self.uncertainty,
            "uncertainty_ref": self.uncertainty_ref,
            "instrument_id": self.instrument_id,
            "calibration_reference": self.calibration_reference,
            "timestamp": self.timestamp,
            "method": self.method,
            "source": self.source,
            "location": self.location,
            "subject": self.subject,
            "operator": self.operator,
            "provenance": self.provenance,
            "evidence": self.evidence,
            "revision": self.revision,
        }
