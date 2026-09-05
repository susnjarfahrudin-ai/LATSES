"""Thermal analysis adapters."""

from .building_model_adapter import ThermalBuildingInput, ThermalWallInput, to_thermal_input
from .room_heat_loss import BuildingThermalResult, RoomHeatLoss, ThermalDesignConditions, calculate_room_heat_losses
from .room_heat_loss import (
    DEFAULT_R_SE_M2K_W,
    DEFAULT_R_SI_M2K_W,
    RoomHeatLossResult,
    calculate_room_heat_losses,
)

__all__ = [
    "ThermalBuildingInput",
    "ThermalWallInput",
    "to_thermal_input",
    "BuildingThermalResult",
    "RoomHeatLoss",
    "ThermalDesignConditions",
    "DEFAULT_R_SE_M2K_W",
    "DEFAULT_R_SI_M2K_W",
    "RoomHeatLossResult",
    "calculate_room_heat_losses",
]
