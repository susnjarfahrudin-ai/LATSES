"""Unified LATCES building-model foundation."""

from .core import BuildingModel, Level, Room, Wall, Opening, Material
from .airflow import AirflowResult, calculate_airflow
from .water import WaterResult, WaterQualityStatus, calculate_water_flow
from .heating import HeatingResult, calculate_heat_load
from .recommendation import Recommendation, Evidence
from .validation import ValidationResult, Status, validate_model

__all__ = [
    "BuildingModel", "Level", "Room", "Wall", "Opening", "Material",
    "AirflowResult", "calculate_airflow", "WaterResult", "WaterQualityStatus",
    "calculate_water_flow", "HeatingResult", "calculate_heat_load",
    "Recommendation", "Evidence", "ValidationResult", "Status", "validate_model",
]
