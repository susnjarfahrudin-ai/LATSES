"""LAT-CES thermal analysis and input-contract package."""

from .building_model_adapter import ThermalBuildingInput, ThermalWallInput, to_thermal_input
from .room_heat_loss import (
    DEFAULT_R_SE_M2K_W,
    DEFAULT_R_SI_M2K_W,
    RoomHeatLossResult,
    calculate_room_heat_losses,
)
from .input_contract import (
    CalculationScope,
    InputStatus,
    IndoorConditionInput,
    InternalGainsInput,
    MaterialThermalInput,
    ThermalBridgeInput,
    ThermalZoneInput,
    TransparentElementInput,
    WeatherInput,
)
from .validation_gate import MissingParameter, ValidationResult, validate_thermal_inputs

__all__ = [
    "ThermalBuildingInput",
    "ThermalWallInput",
    "to_thermal_input",
    "DEFAULT_R_SE_M2K_W",
    "DEFAULT_R_SI_M2K_W",
    "RoomHeatLossResult",
    "calculate_room_heat_losses",
    "CalculationScope",
    "InputStatus",
    "MaterialThermalInput",
    "TransparentElementInput",
    "ThermalBridgeInput",
    "WeatherInput",
    "IndoorConditionInput",
    "InternalGainsInput",
    "ThermalZoneInput",
    "MissingParameter",
    "ValidationResult",
    "validate_thermal_inputs",
]
