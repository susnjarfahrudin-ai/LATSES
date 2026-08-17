"""Canonical fan affinity-law model."""

from lat_ces.core.dimensions import FLOW_RATE, PRESSURE, POWER
from lat_ces.scientific.quantity import PhysicalQuantity


class FanAffinityError(Exception):
    """Raised for invalid fan affinity-law inputs."""


class FanAffinityModel:
    """Scale flow, pressure and power between fan speeds."""

    @staticmethod
    def scale_by_rpm(
        flow: PhysicalQuantity,
        pressure: PhysicalQuantity,
        power: PhysicalQuantity,
        n1_rpm: float,
        n2_rpm: float,
    ):
        if n1_rpm <= 0 or n2_rpm <= 0:
            raise FanAffinityError("RPM values must be positive.")
        if flow.dimension != FLOW_RATE:
            raise FanAffinityError("flow must have flow-rate dimension")
        if pressure.dimension != PRESSURE:
            raise FanAffinityError("pressure must have pressure dimension")
        if power.dimension != POWER:
            raise FanAffinityError("power must have power dimension")

        ratio = n2_rpm / n1_rpm
        q_scale = ratio
        p_scale = ratio**2
        w_scale = ratio**3
        return (
            PhysicalQuantity(flow.value * q_scale, FLOW_RATE, flow.uncertainty * q_scale),
            PhysicalQuantity(pressure.value * p_scale, PRESSURE, pressure.uncertainty * p_scale),
            PhysicalQuantity(power.value * w_scale, POWER, power.uncertainty * w_scale),
        )


__all__ = ["FanAffinityError", "FanAffinityModel"]
