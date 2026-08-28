from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from numbers import Real
from typing import Any
from uuid import uuid4

from lat_ces.scientific.quantity import Quantity

from .provenance import MeasurementProvenance


class MeasurementError(ValueError):
    """Raised when a measurement violates the canonical SCI contract."""


@dataclass(frozen=True)
class Measurement:
    """Canonical scientific measurement record."""

    quantity: Any
    value: Real | None = None
    unit: Any | None = None
    uncertainty: Any = None
    instrument: Any = None
    calibration: Any = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    provenance: MeasurementProvenance | None = None
    evidence: Any = None
    measurement_id: str = field(default_factory=lambda: f"MEAS-{uuid4().hex.upper()}")
    revision: int = 1
    building_model_id: str = ""
    location: object | None = None
    method: str | None = None
    source: str | None = None

    @property
    def resolved_source(self) -> str | None:
        """Canonical source value consumed by the validation contract."""
        return self.source

    def validate(self) -> "Measurement":
        from .validation import validate_measurement
        return validate_measurement(self)

    def revise(
        self,
        *,
        reason: str,
        quantity: Any | None = None,
        uncertainty: Any = None,
        method: str | None = None,
        source: str | None = None,
        calibration: Any = None,
        evidence: Any = None,
    ) -> "Measurement":
        if not reason.strip():
            raise MeasurementError("revision reason must be non-empty")
        return Measurement(
            quantity=quantity or self.quantity,
            value=self.value,
            unit=self.unit,
            uncertainty=self.uncertainty if uncertainty is None else uncertainty,
            instrument=self.instrument,
            calibration=self.calibration if calibration is None else calibration,
            timestamp=datetime.now(timezone.utc).isoformat(),
            provenance=self.provenance,
            evidence=self.evidence if evidence is None else evidence,
            measurement_id=self.measurement_id,
            revision=self.revision + 1,
            building_model_id=self.building_model_id,
            location=self.location,
            method=self.method if method is None else method,
            source=self.source if source is None else source,
        )

    def to_record(self) -> dict[str, Any]:
        return {
            "measurement_id": self.measurement_id,
            "building_model_id": self.building_model_id,
            "quantity": self.quantity.to_record() if hasattr(self.quantity, "to_record") else repr(self.quantity),
            "value": self.value,
            "unit": getattr(self.unit, "symbol", repr(self.unit)),
            "dimension": repr(getattr(self.quantity, "dimension", None)),
            "uncertainty": self.uncertainty.to_record() if hasattr(self.uncertainty, "to_record") else self.uncertainty,
            "instrument": self.instrument.to_record() if hasattr(self.instrument, "to_record") else self.instrument,
            "calibration": self.calibration.to_record() if hasattr(self.calibration, "to_record") else self.calibration,
            "timestamp": self.timestamp,
            "location": self.location,
            "provenance": self.provenance.__dict__ if self.provenance else None,
            "evidence": self.evidence.to_record() if hasattr(self.evidence, "to_record") else self.evidence,
            "method": self.method,
            "source": self.resolved_source,
            "revision": self.revision,
        }


__all__ = ["Measurement", "MeasurementError"]
