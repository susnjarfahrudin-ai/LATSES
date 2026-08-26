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
    """Canonical scientific measurement record.

    ``Quantity`` is accepted as the canonical implementation, while any
    quantity-like scientific object exposing the required ``dimension``
    contract is also valid. This keeps Measurement coupled to the scientific
    contract rather than to one concrete Python class.
    """

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
    method: str = ""
    source: str = ""

    def __post_init__(self) -> None:
        # Measurement depends on the scientific Quantity contract, not on a
        # concrete Python implementation. A structural quantity contract must
        # expose at least a physical dimension; value/unit may either be carried
        # by the quantity or supplied explicitly by the Measurement record.
        if not hasattr(self.quantity, "dimension"):
            raise MeasurementError(
                "Measurement requires a scientific quantity with a dimension"
            )
        if isinstance(self.quantity, Quantity):
            quantity_value = getattr(self.quantity, "value", None)
            quantity_unit = getattr(self.quantity, "unit", None)
        else:
            quantity_value = getattr(self.quantity, "value", None)
            quantity_unit = getattr(self.quantity, "unit", None)

        if self.revision < 1:
            raise MeasurementError("measurement revision must be >= 1")
        if not self.measurement_id.strip():
            raise MeasurementError("measurement_id must be non-empty")
        if not isinstance(self.timestamp, str) or not self.timestamp.strip():
            raise MeasurementError("timestamp must be non-empty")

        if self.value is None:
            if quantity_value is None:
                raise MeasurementError(
                    "Measurement requires a measured value when quantity does not carry one"
                )
            object.__setattr__(self, "value", quantity_value)
        elif quantity_value is not None and self.value != quantity_value:
            raise MeasurementError("measurement.value must match quantity.value")

        if self.unit is None:
            if quantity_unit is None:
                raise MeasurementError(
                    "Measurement requires a unit when quantity does not carry one"
                )
            object.__setattr__(self, "unit", quantity_unit)
        elif quantity_unit is not None and self.unit is not quantity_unit and self.unit != quantity_unit:
            raise MeasurementError("measurement.unit must match quantity.unit")

        if self.uncertainty is not None:
            uncertainty_value = getattr(self.uncertainty, "value", self.uncertainty)
            if uncertainty_value < 0:
                raise MeasurementError("measurement uncertainty cannot be negative")

    @classmethod
    def now(
        cls,
        quantity: Any,
        *,
        uncertainty: Any = None,
        instrument: Any = None,
        calibration: Any = None,
        provenance: MeasurementProvenance | None = None,
        evidence: Any = None,
        method: str = "",
        source: str = "",
        measurement_id: str | None = None,
    ) -> "Measurement":
        return cls(
            quantity=quantity,
            uncertainty=uncertainty,
            instrument=instrument,
            calibration=calibration,
            provenance=provenance,
            evidence=evidence,
            method=method,
            source=source,
            measurement_id=measurement_id or f"MEAS-{uuid4().hex.upper()}",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    @property
    def dimension(self):
        return self.quantity.dimension

    @property
    def revision_label(self) -> str:
        n = self.revision
        parts: list[str] = []
        while n:
            n, rem = divmod(n - 1, 26)
            parts.append(chr(65 + rem))
        return "".join(reversed(parts))

    @property
    def resolved_source(self) -> str:
        return self.source.strip() or (self.provenance.source if self.provenance else "") or getattr(self.instrument, "instrument_id", "") or getattr(self.instrument, "uuid", "")

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
            uncertainty=self.uncertainty if uncertainty is None else uncertainty,
            instrument=self.instrument,
            calibration=self.calibration if calibration is None else calibration,
            timestamp=datetime.now(timezone.utc).isoformat(),
            provenance=self.provenance,
            evidence=self.evidence if evidence is None else evidence,
            measurement_id=self.measurement_id,
            revision=self.revision + 1,
            method=self.method if method is None else method,
            source=self.source if source is None else source,
        )

    def to_record(self) -> dict[str, Any]:
        return {
            "measurement_id": self.measurement_id,
            "quantity": self.quantity.to_record() if hasattr(self.quantity, "to_record") else repr(self.quantity),
            "value": self.value,
            "unit": getattr(self.unit, "symbol", repr(self.unit)),
            "dimension": repr(self.dimension),
            "uncertainty": self.uncertainty.to_record() if hasattr(self.uncertainty, "to_record") else self.uncertainty,
            "instrument": self.instrument.to_record() if hasattr(self.instrument, "to_record") else self.instrument,
            "calibration": self.calibration.to_record() if hasattr(self.calibration, "to_record") else self.calibration,
            "timestamp": self.timestamp,
            "method": self.method,
            "source": self.resolved_source,
            "provenance": self.provenance.__dict__ if self.provenance else None,
            "evidence": self.evidence.to_record() if hasattr(self.evidence, "to_record") else self.evidence,
            "revision": self.revision,
        }


__all__ = ["Measurement", "MeasurementError"]
