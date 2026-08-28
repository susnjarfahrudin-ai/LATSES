from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from .provenance import MeasurementProvenance


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
    building_model_id: str = ""
    location: object | None = None

    def validate(self) -> "Measurement":
        from .validation import validate_measurement

        return validate_measurement(self)

    def to_record(self) -> dict[str, object]:
        return {
            "measurement_id": self.measurement_id,
            "building_model_id": self.building_model_id,
            "quantity": self.quantity,
            "value": self.value,
            "unit": self.unit,
            "uncertainty": self.uncertainty,
            "instrument": self.instrument,
            "calibration": self.calibration,
            "timestamp": self.timestamp,
            "location": self.location,
            "provenance": self.provenance,
            "evidence": self.evidence,
            "revision": self.revision,
        }
