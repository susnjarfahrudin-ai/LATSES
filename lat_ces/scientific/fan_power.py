"""Canonical fan-power model for the LAT-CES fluid stack."""

from lat_ces.core.dimensions import FLOW_RATE, PRESSURE, POWER
from lat_ces.scientific.quantity import PhysicalQuantity


class FanPowerError(ValueError):
    """Raised for invalid fan-power inputs."""


class FanPowerModel:
    """Compute fan shaft/input power from flow, pressure drop and efficiency."""

    @staticmethod
    def _require_dimension(quantity: PhysicalQuantity, expected, name: str) -> None:
        if quantity.dimension != expected:
            raise FanPowerError(
                f"{name} must have dimension {expected}, got {quantity.dimension}"
            )

    @classmethod
    def calculate(
        cls,
        flow_rate: PhysicalQuantity,
        pressure_drop: PhysicalQuantity,
        efficiency: float = 1.0,
    ) -> PhysicalQuantity:
        if efficiency <= 0.0 or efficiency > 1.0:
            raise FanPowerError("Efficiency must be in the range (0, 1.0].")
        cls._require_dimension(flow_rate, FLOW_RATE, "flow_rate")
        cls._require_dimension(pressure_drop, PRESSURE, "pressure_drop")
        raw_power = flow_rate * pressure_drop
        return PhysicalQuantity(
            value=raw_power.value / efficiency,
            dimension=POWER,
            uncertainty=raw_power.uncertainty / efficiency,
        )


__all__ = ["FanPowerError", "FanPowerModel"]
