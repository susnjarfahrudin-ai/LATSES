"""Unified LATCES building-model foundation."""

from .core import BuildingModel, Level, Room, Wall, Opening, Material
from .airflow import AirflowResult, calculate_airflow
from .water import WaterResult, WaterQualityStatus, calculate_water_flow
from .heating import HeatingResult, calculate_heat_load
from .systems import VentilationOpening, WaterBranch, HeatingZone
from .integration import BuildingEngineeringReport, RoomEngineeringResult, analyze_building
from .recommendation import Recommendation, Evidence
from .validation import ValidationResult, Status, validate_model
from .concept import (
    BuildingConcept, ConstructionKind, InsulationKind, LevelKind, MaterialSelection,
    MEPSystem, OpeningSpec, RoofCover, RoofCoverSpec, RoofModel, RoofShape,
    RoofStructure, RoofSubstructure, RoofSupport, StructuralLoadInput, SystemNode,
    WindowMaterial,
)
from .concept_adapter import to_concept

__all__ = [
    "BuildingModel", "Level", "Room", "Wall", "Opening", "Material",
    "AirflowResult", "calculate_airflow",
    "WaterResult", "WaterQualityStatus", "calculate_water_flow",
    "HeatingResult", "calculate_heat_load", "VentilationOpening", "WaterBranch",
    "HeatingZone", "BuildingEngineeringReport", "RoomEngineeringResult",
    "analyze_building", "Recommendation", "Evidence", "ValidationResult",
    "Status", "validate_model", "BuildingConcept", "ConstructionKind",
    "InsulationKind", "LevelKind", "MaterialSelection", "MEPSystem", "OpeningSpec",
    "RoofCover", "RoofCoverSpec", "RoofModel", "RoofShape", "RoofStructure",
    "RoofSubstructure", "RoofSupport", "StructuralLoadInput", "SystemNode",
    "WindowMaterial", "to_concept",
]
