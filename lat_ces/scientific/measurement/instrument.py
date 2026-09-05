from __future__ import annotations

from dataclasses import dataclass
from numbers import Real
from typing import Any

from lat_ces.scientific.units.core import Unit


class InstrumentValidationError(ValueError):
    """Raised when an instrument violates the SCI-CORE-0046 contract."""


@dataclass(frozen=True)
class Instrument:
    """Canonical measurement instrument scientific object."""

    instrument_id: str
    name: str
    measurement_range: tuple[float, float]
    accuracy: float
    manufacturer: str | None = None
    unit: Unit | None = None
    calibration_required: bool = True

    def __post_init__(self) -> None:
        if not self.instrument_id.strip():
            raise InstrumentValidationError("instrument_id must be non-empty")
        if not self.name.strip():
            raise InstrumentValidationError("instrument name must be non-empty")
        if len(self.measurement_range) != 2 or self.measurement_range[0] >= self.measurement_range[1]:
            raise InstrumentValidationError("measurement_range must be an increasing pair")
        if not isinstance(self.accuracy, Real) or self.accuracy < 0:
            raise InstrumentValidationError("instrument accuracy must be non-negative")

    def validate_value(self, value: Real) -> None:
        if not self.measurement_range[0] <= value <= self.measurement_range[1]:
            raise InstrumentValidationError(
                f"measurement value {value!r} is outside instrument range {self.measurement_range!r}"
            )

    def to_record(self) -> dict[str, Any]:
        return {
            "instrument_id": self.instrument_id,
            "name": self.name,
            "measurement_range": list(self.measurement_range),
            "accuracy": float(self.accuracy),
            "manufacturer": self.manufacturer,
            "unit": getattr(self.unit, "symbol", None),
            "calibration_required": self.calibration_required,
        }


__all__ = ["Instrument", "InstrumentValidationError"]
