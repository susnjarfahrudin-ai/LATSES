"""Structural read-only projection from the canonical Building Model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lat_ces.building_model.source_of_truth import build_read_only_views


@dataclass(frozen=True)
class StaticWallInput:
    wall_id: str
    product_id: str
    room_ids: tuple[str, ...]
    thickness_m: float
    load_bearing: bool
    density_kg_m3: float
    compressive_strength_mpa: float

    @property
    def self_weight_density_kg_m3(self) -> float:
        return self.density_kg_m3


@dataclass(frozen=True)
class StaticBuildingInput:
    walls: tuple[StaticWallInput, ...]


def to_static_input(model: Any) -> StaticBuildingInput:
    """Create immutable structural inputs from canonical Building Model views."""
    views = build_read_only_views(model)
    materials = {view.product_id: view for view in views.material_views}
    walls: list[StaticWallInput] = []
    for wall in views.wall_views:
        material = materials[wall.product_id]
        walls.append(
            StaticWallInput(
                wall_id=wall.wall_id,
                product_id=wall.product_id,
                room_ids=wall.room_ids,
                thickness_m=wall.thickness_m,
                load_bearing=wall.load_bearing,
                density_kg_m3=material.density_kg_m3,
                compressive_strength_mpa=material.compressive_strength_mpa,
            )
        )
    return StaticBuildingInput(tuple(walls))
