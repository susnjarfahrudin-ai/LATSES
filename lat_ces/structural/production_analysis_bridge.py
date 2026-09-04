"""Explicit bridge from the production BuildingModel to structural input."""
from __future__ import annotations

from dataclasses import dataclass

from lat_ces.building.model import BuildingModel
from lat_ces.structural.building_model_adapter import StaticBuildingInput, to_static_input


@dataclass(frozen=True)
class ProductionStructuralAnalysisInput:
    """Immutable structural input projected from the canonical production model."""

    model: BuildingModel
    building: StaticBuildingInput


def to_production_structural_input(model: BuildingModel) -> ProductionStructuralAnalysisInput:
    """Project one exact production BuildingModel into structural read-only input."""
    if not isinstance(model, BuildingModel):
        raise TypeError("model must be a production BuildingModel")
    return ProductionStructuralAnalysisInput(model=model, building=to_static_input(model))


__all__ = ["ProductionStructuralAnalysisInput", "to_production_structural_input"]
