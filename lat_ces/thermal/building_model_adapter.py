"""Read-only thermal projection from the canonical production BuildingModel."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lat_ces.building_model.source_of_truth import build_read_only_views


@dataclass(frozen=True)
class ThermalWallInput:
    wall_id: str
    product_id: str
    thickness_m: float
    thermal_conductivity_w_mk: float | None

    @property
    def conductive_resistance_m2kw(self) -> float:
        if self.thermal_conductivity_w_mk is None or self.thermal_conductivity_w_mk <= 0:
            raise ValueError("thermal conductivity must be positive")
        return self.thickness_m / self.thermal_conductivity_w_mk


@dataclass(frozen=True)
class ThermalBuildingInput:
    walls: tuple[ThermalWallInput, ...]


def to_thermal_input(model: Any) -> ThermalBuildingInput:
    """Create immutable thermal inputs from the production BuildingModel."""
    views = build_read_only_views(model)
    materials = {view.product_id: view for view in views.material_views}
    return ThermalBuildingInput(
        tuple(
            ThermalWallInput(
                wall_id=wall.wall_id,
                product_id=wall.product_id,
                thickness_m=wall.thickness_m,
                thermal_conductivity_w_mk=materials[wall.product_id].thermal_conductivity_w_mk,
            )
            for wall in views.wall_views
        )
    )
