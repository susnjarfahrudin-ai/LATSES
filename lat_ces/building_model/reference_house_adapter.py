"""Canonical boundary between the Reference House fixture and BuildingModel.

The current Reference House fixture is intentionally richer in engineering
metadata than in editable room geometry: it stores room areas, but does not
store room length/width or explicit wall lines. This adapter therefore refuses
to invent geometry. Once the fixture carries canonical geometry, this boundary
is the only place that should construct the BuildingModel instance.
"""
from __future__ import annotations

from dataclasses import dataclass

from lat_ces.reference_house import ReferenceHouse

from .core import BuildingModel, Level


@dataclass(frozen=True)
class ReferenceHouseGeometryGap:
    level_id: str
    room_id: str
    reason: str


class ReferenceHouseGeometryError(ValueError):
    """Raised when the fixture lacks geometry required for canonical mapping."""


def map_reference_house_to_building_model(
    reference_house: ReferenceHouse,
    *,
    strict_geometry: bool = True,
) -> BuildingModel:
    """Map only explicit Reference House geometry into the canonical BuildingModel.

    The current fixture defines the building envelope and level stack, but room
    records contain area/height only. Strict mode therefore fails instead of
    inventing room dimensions or wall lines. Non-strict mode maps only explicit
    level geometry and leaves the room graph empty.
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
        model.add_level(
            Level(
                level_data["id"],
                level_data["name"],
                dimensions["length_m"],
                dimensions["width_m"],
                dimensions["level_height_m"],
            )
        )
    return model


__all__ = [
    "ReferenceHouseGeometryError",
    "ReferenceHouseGeometryGap",
    "map_reference_house_to_building_model",
]
