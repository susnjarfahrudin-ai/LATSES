from __future__ import annotations

import uuid
from typing import Optional

from lat_ces.core.dimensions import LENGTH, MASS, TIME, Unit
from lat_ces.scientific.quantity import PhysicalQuantity


class OutOfRangeError(Exception):
    """Raised when a measurement is outside the device operating range."""


class AccuracySpec:
    """Legacy accuracy specification kept as a compatibility facade."""

    def __init__(self, relative_error: float = 0.0, absolute_error: float = 0.0):
        if relative_error < 0.0 or absolute_error < 0.0:
            raise ValueError("Greške u specifikaciji tačnosti ne mogu biti negativne.")
        self.relative_error = float(relative_error)
        self.absolute_error = float(absolute_error)

    def calculate_uncertainty(self, measured_value: float) -> float:
        return self.absolute_error + self.relative_error * abs(measured_value)


class MeasurementDevice:
    """Legacy measurement-device facade retained for existing consumers."""

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
    meter_per_second = Unit("meter per second", "m/s", LENGTH / TIME)
    accuracy = AccuracySpec(relative_error=0.015, absolute_error=0.1)
    return MeasurementDevice(
        name, "Pitot Tube", meter_per_second, accuracy, min_range=1.0, max_range=40.0
    )


def create_diff_pressure_sensor(name: str = "Plenum DP Sensor") -> MeasurementDevice:
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
