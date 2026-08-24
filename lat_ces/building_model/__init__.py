"""Unified LATCES building-model foundation."""

from .core import BuildingModel, Level, Room, Wall, Opening, Material
from .example_model import make_small_reference_house
from .airflow import AirflowResult, calculate_airflow
from .water import WaterResult, WaterQualityStatus, calculate_water_flow
from .heating import HeatingResult, calculate_heat_load
from .systems import VentilationOpening, WaterBranch, HeatingZone
from .integration import BuildingEngineeringReport, RoomEngineeringResult, analyze_building
from .recommendation import Recommendation, Evidence
from .validation import ValidationResult, Status, validate_model
from .concept import (
    BuildingConcept,
    ConstructionKind,
    InsulationKind,
    LevelKind,
    MaterialSelection,
    MEPSystem,
    OpeningSpec,
    RoofCover,
    RoofCoverSpec,
    RoofModel,
    RoofShape,
    RoofStructure,
    RoofSubstructure,
    RoofSupport,
    StructuralLoadInput,
    SystemNode,
    WindowMaterial,
)

__all__ = [
    "BuildingModel", "Level", "Room", "Wall", "Opening", "Material",
    "make_small_reference_house",
    "AirflowResult", "calculate_airflow", "WaterResult", "WaterQualityStatus",
    "calculate_water_flow", "HeatingResult", "calculate_heat_load",
    "VentilationOpening", "WaterBranch", "HeatingZone",
    "BuildingEngineeringReport", "RoomEngineeringResult", "analyze_building",
    "Recommendation", "Evidence", "ValidationResult", "Status", "validate_model",
    "BuildingConcept", "ConstructionKind", "InsulationKind", "LevelKind",
    "MaterialSelection", "MEPSystem", "OpeningSpec", "RoofCover", "RoofCoverSpec",
    "RoofModel", "RoofShape", "RoofStructure", "RoofSubstructure", "RoofSupport",
    "StructuralLoadInput", "SystemNode", "WindowMaterial",
]
