from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from .provenance import MeasurementProvenance


class MeasurementError(ValueError):
    """Base error for invalid canonical Measurement records."""


@dataclass(frozen=True)
class Measurement:
    """SCI-0046/0047 canonical measurement object.

    A measurement is a traceable scientific record, not a bare number.
    """

    quantity: object
    value: float
    unit: object
    uncertainty: float | None
    instrument: object
    calibration: object | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    provenance: MeasurementProvenance | None = None
    evidence: object | None = None
    measurement_id: str = field(default_factory=lambda: f"MEAS-{uuid4().hex.upper()}")
    revision: int = 1

    @classmethod
    def now(cls, quantity, *, method: str, source: str, instrument_id: str | None = None,
            location: str | None = None, subject: str | None = None,
            calibration_reference: str | None = None, operator: str | None = None,
            uncertainty_ref: str | None = None, evidence=None) -> "Measurement":
        """Create a canonical contextual measurement from a Quantity."""
        value = getattr(quantity, "value", None)
        unit = getattr(quantity, "unit", None)
        if value is None or unit is None:
            raise MeasurementError("Measurement.now requires a canonical Quantity with value and unit")
        return cls(
            quantity=quantity,
            value=float(value),
            unit=unit,
            uncertainty=uncertainty_ref,
            instrument=instrument_id,
            calibration=calibration_reference,
            provenance=MeasurementProvenance(
                method=method,
                source=source,
                location=location,
                subject=subject,
                operator=operator,
            ),
            evidence=evidence,
        )

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
            "instrument": self.instrument,
            "calibration": self.calibration,
            "timestamp": self.timestamp,
            "provenance": self.provenance,
            "evidence": self.evidence,
            "revision": self.revision,
        }
