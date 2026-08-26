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
        quantity,
        timestamp: str,
        method: str,
        source: str,
        *,
        instrument_id: str | None = None,
        location: str | None = None,
        subject: str | None = None,
        calibration_reference: str | None = None,
        operator: str | None = None,
        uncertainty_ref: str | None = None,
        uncertainty: float | None = None,
        provenance=None,
        evidence=None,
        measurement_id: str | None = None,
        revision: int = 1,
    ) -> None:
        if quantity is None or not hasattr(quantity, "value") or not hasattr(quantity, "unit"):
            raise TypeError("Measurement requires a canonical Quantity")
        if not timestamp:
            raise MeasurementError("Measurement requires a timestamp")
        if not method:
            raise MeasurementError("Measurement requires a method")
        if not source:
            raise MeasurementError("Measurement requires a source")
        if uncertainty is not None and float(uncertainty) < 0:
            raise MeasurementError("Measurement uncertainty cannot be negative")
        if revision < 1:
            raise MeasurementError("Measurement revision must be >= 1")

        object.__setattr__(self, "quantity", quantity)
        object.__setattr__(self, "timestamp", timestamp)
        object.__setattr__(self, "method", method)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "instrument_id", instrument_id)
        object.__setattr__(self, "location", location)
        object.__setattr__(self, "subject", subject)
        object.__setattr__(self, "calibration_reference", calibration_reference)
        object.__setattr__(self, "operator", operator)
        object.__setattr__(self, "uncertainty_ref", uncertainty_ref)
        object.__setattr__(self, "value", quantity.value)
        object.__setattr__(self, "unit", quantity.unit)
        object.__setattr__(
            self,
            "uncertainty",
            float(uncertainty) if uncertainty is not None else getattr(quantity, "uncertainty", None),
        )
        object.__setattr__(
            self,
            "provenance",
            provenance if provenance is not None else getattr(quantity, "provenance", None),
        )
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(
            self,
            "measurement_id",
            measurement_id or f"LAT-MEAS-{uuid4().hex.upper()}",
        )
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
