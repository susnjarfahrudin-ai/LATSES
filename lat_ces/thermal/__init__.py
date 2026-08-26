"""Thermal analysis adapters."""

from .building_model_adapter import ThermalBuildingInput, ThermalWallInput, to_thermal_input
from .room_heat_loss import BuildingThermalResult, RoomHeatLoss, ThermalDesignConditions, calculate_room_heat_losses

__all__ = [
    "ThermalBuildingInput",
    "ThermalWallInput",
    "to_thermal_input",
    "BuildingThermalResult",
    "RoomHeatLoss",
    "ThermalDesignConditions",
    "calculate_room_heat_losses",
]
