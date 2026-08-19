"""Compatibility facade for the legacy scalar fan-affinity API.

Canonical fan-affinity physics lives in ``lat_ces.scientific.fan_laws``.
This module preserves the older constructor/``scale_performance`` contract
without maintaining a second implementation of the affinity laws.
"""

from lat_ces.core.dimensions import FLOW_RATE, POWER, PRESSURE
from lat_ces.scientific.fan_laws import FanAffinityError as CanonicalFanAffinityError
from lat_ces.scientific.fan_laws import FanAffinityModel as CanonicalFanAffinityModel
from lat_ces.scientific.quantity import PhysicalQuantity


class FanAffinityError(CanonicalFanAffinityError):
    """Backward-compatible error type for the legacy scalar API."""


class FanAffinityModel:
    """Legacy scalar facade delegating all affinity-law physics canonically."""

    def __init__(self, base_rpm: float, base_flow: float, base_pressure: float, base_power: float):
        if base_rpm <= 0.0 or base_flow < 0.0 or base_pressure < 0.0 or base_power < 0.0:
            raise FanAffinityError(
                "Base parameters must be valid non-negative values, RPM must be positive."
            )
        self.base_rpm = float(base_rpm)
        self.base_flow = float(base_flow)
        self.base_pressure = float(base_pressure)
        self.base_power = float(base_power)

    def scale_performance(self, new_rpm: float) -> tuple[float, float, float]:
        """Preserve the legacy scalar API while delegating to the canonical model."""
        if new_rpm < 0.0:
            raise FanAffinityError("New RPM cannot be negative.")

        flow = PhysicalQuantity(self.base_flow, dimension=FLOW_RATE)
        pressure = PhysicalQuantity(self.base_pressure, dimension=PRESSURE)
        power = PhysicalQuantity(self.base_power, dimension=POWER)

        try:
            scaled_flow, scaled_pressure, scaled_power = CanonicalFanAffinityModel.scale_by_rpm(
                flow,
                pressure,
                power,
                self.base_rpm,
                float(new_rpm),
            )
        except CanonicalFanAffinityError as exc:
            raise FanAffinityError(str(exc)) from exc

        return (
            round(scaled_flow.value, 3),
            round(scaled_pressure.value, 2),
            round(scaled_power.value, 3),
        )


__all__ = ["FanAffinityError", "FanAffinityModel", "CanonicalFanAffinityModel"]
