from __future__ import annotations

import uuid
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Any, Optional

from lat_ces.core.dimensions import LENGTH, MASS, TIME, Unit
from lat_ces.scientific.quantity import PhysicalQuantity, Quantity


class MeasurementError(ValueError):
    """Raised when a canonical Measurement violates its contract."""


class OutOfRangeError(Exception):
    """Raised when a measurement is outside the device operating range."""


class AccuracySpec:
    """Accuracy specification combining relative and fixed absolute error."""

    def __init__(self, relative_error: float = 0.0, absolute_error: float = 0.0):
        if relative_error < 0.0 or absolute_error < 0.0:
            raise ValueError("Greške u specifikaciji tačnosti ne mogu biti negativne.")
        self.relative_error = float(relative_error)
        self.absolute_error = float(absolute_error)

    def calculate_uncertainty(self, measured_value: float) -> float:
        """Calculate absolute uncertainty for a measured value."""
        return self.absolute_error + self.relative_error * abs(measured_value)


@dataclass(frozen=True)
class Measurement:
    """Observed canonical Quantity with explicit measurement context."""

    quantity: Quantity
    measured_at: str
    method: str
    source: str
    measurement_id: str = ""
    instrument_id: Optional[str] = None
    location: Optional[str] = None
    subject: Optional[str] = None
    calibration_reference: Optional[str] = None
    operator: Optional[str] = None
    uncertainty_ref: Any = None

    def __post_init__(self) -> None:
        if not isinstance(self.quantity, Quantity):
            raise TypeError("Measurement.quantity must be a canonical Quantity")
        for field_name in ("measured_at", "method", "source"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise MeasurementError(f"{field_name} must be a non-empty string")
        if not self.measurement_id:
            object.__setattr__(self, "measurement_id", f"LAT-MEAS-{uuid.uuid4()}")

    @classmethod
    def now(
        cls,
        quantity: Quantity,
        *,
        method: str,
        source: str,
        instrument_id: Optional[str] = None,
        location: Optional[str] = None,
        subject: Optional[str] = None,
        calibration_reference: Optional[str] = None,
        operator: Optional[str] = None,
        uncertainty_ref: Any = None,
    ) -> "Measurement":
        return cls(
            quantity=quantity,
            measured_at=datetime.now(timezone.utc).isoformat(),
            method=method,
            source=source,
            instrument_id=instrument_id,
            location=location,
            subject=subject,
            calibration_reference=calibration_reference,
            operator=operator,
            uncertainty_ref=uncertainty_ref,
        )

    @property
    def value(self):
        return self.quantity.value

    @property
    def unit(self):
        return self.quantity.unit

    @property
    def dimension(self):
        return self.quantity.dimension

    @property
    def provenance(self) -> Any:
        return self.quantity.provenance


class MeasurementDevice:
    """Legacy-compatible measurement instrument producing PhysicalQuantity."""

    def __init__(
        self,
        name: str,
        device_type: str,
        unit: Unit,
        accuracy_spec: AccuracySpec,
        min_range: float,
        max_range: float,
        calibration_offset: float = 0.0,
        sko_uuid: Optional[str] = None,
    ):
        if min_range >= max_range:
            raise ValueError("Minimalni opseg mora biti manji od maksimalnog.")

        self.name = name
        self.device_type = device_type
        self.unit = unit
        self.accuracy_spec = accuracy_spec
        self.min_range = float(min_range)
        self.max_range = float(max_range)
        self.calibration_offset = float(calibration_offset)
        self.uuid = sko_uuid or str(uuid.uuid4())

    def measure(self, raw_value: float) -> PhysicalQuantity:
        """Return a calibrated legacy PhysicalQuantity."""
        if not self.min_range <= raw_value <= self.max_range:
            raise OutOfRangeError(
                f"Očitanje {raw_value} {self.unit.symbol} je izvan radnog opsega "
                f"instrumenta '{self.name}' [{self.min_range}, {self.max_range}]."
            )

        corrected_value = raw_value - self.calibration_offset
        uncertainty = self.accuracy_spec.calculate_uncertainty(corrected_value)

        return PhysicalQuantity(
            value=corrected_value,
            uncertainty=uncertainty,
            unit=self.unit,
            sko_uuid=self.uuid,
        )

    def __repr__(self) -> str:
        return (
            f"<MeasurementDevice '{self.name}' ({self.device_type}): "
            f"[{self.min_range} - {self.max_range}] {self.unit.symbol}>"
        )


def create_pitot_tube(name: str = "Standard Pitot Tube") -> MeasurementDevice:
    """Create a standard Pitot-Prandtl airflow velocity instrument."""
    meter_per_second = Unit("meter per second", "m/s", LENGTH / TIME)
    accuracy = AccuracySpec(relative_error=0.015, absolute_error=0.1)
    return MeasurementDevice(
        name,
        "Pitot Tube",
        meter_per_second,
        accuracy,
        min_range=1.0,
        max_range=40.0,
    )


def create_diff_pressure_sensor(name: str = "Plenum DP Sensor") -> MeasurementDevice:
    """Create a differential-pressure transmitter for ducts and plenums."""
    pascal = Unit("pascal", "Pa", MASS / (LENGTH * (TIME**2)))
    accuracy = AccuracySpec(relative_error=0.005, absolute_error=1.0)
    return MeasurementDevice(
        name,
        "Differential Pressure Transmitter",
        pascal,
        accuracy,
        min_range=0.0,
        max_range=2000.0,
    )


__all__ = [
    "Measurement",
    "MeasurementError",
    "AccuracySpec",
    "MeasurementDevice",
    "OutOfRangeError",
    "create_pitot_tube",
    "create_diff_pressure_sensor",
]
