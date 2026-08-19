"""LAT-CES Module 015 compatibility facade.

Canonical physics lives in ``lat_ces.scientific.pressure_drop`` and
``lat_ces.scientific.fan_power``. This namespace preserves legacy APIs.
"""
from lat_ces.core.dimensions import FLOW_RATE, POWER, PRESSURE
from lat_ces.scientific.fan_power import FanPowerError, FanPowerModel
from lat_ces.scientific.pressure_drop import PressureDropModel, PressureError


class PressureDropEngine:
    """Legacy adapter for the canonical pressure-drop model."""

    def __init__(self, loss_coefficient: float, air_density: float = 1.2):
        self._model = PressureDropModel(
            loss_coefficient=loss_coefficient,
            air_density=air_density,
        )

    def compute_pressure_drop(self, velocity: float) -> float:
        return self._model.compute_pressure_drop(velocity)

    def compute_quantity_pressure_drop(self, velocity, density=None):
        return self._model.compute_quantity_pressure_drop(velocity, density)


class FanEngine:
    """Compatibility facade for the canonical fan-power model."""

    def calculate_fan_power(self, flow_rate, pressure_drop, efficiency: float = 1.0):
        try:
            return FanPowerModel.calculate(flow_rate, pressure_drop, efficiency)
        except FanPowerError as exc:
            raise ValueError(str(exc)) from exc


__all__ = [
    "FLOW_RATE",
    "POWER",
    "PRESSURE",
    "FanEngine",
    "PressureDropEngine",
    "PressureDropModel",
    "PressureError",
    "FanPowerError",
    "FanPowerModel",
]
