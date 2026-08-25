"""Canonical boundary between the Reference House fixture and BuildingModel.

The fixture currently contains explicit building-envelope dimensions, so the
adapter can safely construct the four exterior walls of every level. Room
areas are still not enough to infer room rectangles, interior walls or
individual openings; strict mode therefore continues to reject the room graph
until that geometry is explicitly supplied by the fixture.
"""
from __future__ import annotations

from dataclasses import dataclass

from lat_ces.reference_house import ReferenceHouse

from .core import BuildingModel, Level, Material, Wall


@dataclass(frozen=True)
class ReferenceHouseGeometryGap:
    level_id: str
    room_id: str
    reason: str


class ReferenceHouseGeometryError(ValueError):
    """Raised when the fixture lacks geometry required for canonical mapping."""


def _add_explicit_envelope_walls(level: Level, *, wall_thickness_m: float = 0.25) -> None:
    """Add the four exterior walls implied directly by the 12 m x 10 m envelope."""
    wall_specs = (
        ("south", level.length_m),
        ("east", level.width_m),
        ("north", level.length_m),
        ("west", level.width_m),
    )
    for wall_id, length_m in wall_specs:
        level.add_wall(
            Wall(
                id=f"{level.id}-EXT-{wall_id.upper()}",
                length_m=length_m,
                thickness_m=wall_thickness_m,
                height_m=level.height_m,
                material=Material(name="masonry block 250 mm"),
            )
        )


def map_reference_house_to_building_model(
    reference_house: ReferenceHouse,
    *,
    strict_geometry: bool = True,
) -> BuildingModel:
    """Map only explicit Reference House geometry into the canonical BuildingModel.

    The fixture defines the building envelope and level stack, so exterior walls
    are constructed deterministically. Room records still contain area/height
    only. Strict mode therefore fails instead of inventing room dimensions,
    interior wall lines or openings.
    """
    gaps = tuple(
        ReferenceHouseGeometryGap(level["id"], room["id"], "room length/width geometry is not present")
        for level in reference_house.levels
        for room in level["rooms"]
        if "length_m" not in room or "width_m" not in room
    )
    if strict_geometry and gaps:
        first = gaps[0]
        raise ReferenceHouseGeometryError(
            f"Reference House cannot be mapped to canonical room geometry: "
            f"{first.level_id}/{first.room_id}: {first.reason}"
        )

    dimensions = reference_house.data["dimensions"]
    model = BuildingModel(name=reference_house.data["name"])
    for level_data in reference_house.levels:
        level = Level(
            level_data["id"],
            level_data["name"],
            dimensions["length_m"],
            dimensions["width_m"],
            dimensions["level_height_m"],
        )
        _add_explicit_envelope_walls(level)
        model.add_level(level)
    return model


__all__ = [
    "ReferenceHouseGeometryError",
    "ReferenceHouseGeometryGap",
    "map_reference_house_to_building_model",
]
