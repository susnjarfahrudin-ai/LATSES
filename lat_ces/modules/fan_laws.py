"""Compatibility facade for the canonical fan affinity-law model."""

from lat_ces.core.dimensions import FLOW_RATE, PRESSURE, POWER
from lat_ces.scientific.fan_laws import FanAffinityError, FanAffinityModel
from lat_ces.scientific.quantity import PhysicalQuantity


class FanAffinityEngine:
    """Backward-compatible API delegating to the canonical scientific model."""

    @staticmethod
    def scale_by_rpm(
        flow: PhysicalQuantity,
        pressure: PhysicalQuantity,
        power: PhysicalQuantity,
        n1_rpm: float,
        n2_rpm: float,
    ):
        return FanAffinityModel.scale_by_rpm(
            flow, pressure, power, n1_rpm, n2_rpm
        )


__all__ = ["FanAffinityEngine", "FanAffinityError", "FanAffinityModel"]
