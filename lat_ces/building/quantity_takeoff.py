"""Geometry-driven quantity take-off from the canonical BuildingModel."""
from __future__ import annotations

from dataclasses import dataclass
import math

from .model import BuildingModel


@dataclass(frozen=True)
class LevelQuantity:
    level_id: str
    name: str
    floor_area_m2: float
    volume_m3: float
    wall_length_m: float
    wall_area_m2: float
    opening_area_m2: float
    room_count: int


@dataclass(frozen=True)
class BuildingQuantityTakeoff:
    floor_area_m2: float
    volume_m3: float
    wall_length_m: float
    wall_area_m2: float
    opening_area_m2: float
    roof_plan_area_m2: float
    roof_surface_area_m2: float
    roof_perimeter_m: float
    insulation_area_m2: float
    plaster_area_m2: float
    gutter_length_m: float
    railing_length_m: float
    timber_or_roof_element_count: int
    room_count: int
    levels: tuple[LevelQuantity, ...]


def _level_quantity(level) -> LevelQuantity:
    plan = level.floor_plan
    walls = () if plan is None else tuple(plan.walls.values())
    wall_length = sum(wall.segment.length for wall in walls)
    wall_area = wall_length * level.height
    opening_area = sum(opening.width * opening.height_m for wall in walls for opening in wall.openings)
    return LevelQuantity(
        level_id=level.level_id,
        name=level.name,
        floor_area_m2=level.floor_area,
        volume_m3=level.volume,
        wall_length_m=wall_length,
        wall_area_m2=max(0.0, wall_area),
        opening_area_m2=max(0.0, min(opening_area, wall_area)),
        room_count=len(level.rooms),
    )


def calculate_quantity_takeoff(model: BuildingModel) -> BuildingQuantityTakeoff:
    """Calculate quantities only from geometry/state already present in model."""
    levels = tuple(_level_quantity(level) for level in model.levels.values())
    roof = model.roof
    roof_plan_area = 0.0 if roof is None else roof.plan_area_m2
    roof_surface = 0.0
    roof_perimeter = 0.0
    if roof is not None:
        slope_rad = math.radians(roof.slope_deg)
        roof_surface = roof_plan_area / max(math.cos(slope_rad), 1e-9)
        roof_perimeter = 2.0 * (roof.length_m + roof.width_m)

    insulation_area = sum(max(0.0, item.wall_area_m2 - item.opening_area_m2) for item in levels if any(
        level.level_id == item.level_id and level.insulation_thickness_m > 0.0
        for level in model.levels.values()
    ))
    plaster_area = sum(max(0.0, item.wall_area_m2 - item.opening_area_m2) for item in levels if any(
        level.level_id == item.level_id and level.interior_plaster_thickness_m > 0.0
        for level in model.levels.values()
    ))

    elements = model.all_elements()
    element_types = [element.element_type.casefold() for element in elements]
    railing_length = sum(element.geometry.length for element in elements if "rail" in element.element_type.casefold())
    timber_or_roof_count = sum(
        1 for element_type in element_types if any(token in element_type for token in ("timber", "roof", "krov", "drvo"))
    )

    return BuildingQuantityTakeoff(
        floor_area_m2=sum(item.floor_area_m2 for item in levels),
        volume_m3=sum(item.volume_m3 for item in levels),
        wall_length_m=sum(item.wall_length_m for item in levels),
        wall_area_m2=sum(item.wall_area_m2 for item in levels),
        opening_area_m2=sum(item.opening_area_m2 for item in levels),
        roof_plan_area_m2=roof_plan_area,
        roof_surface_area_m2=roof_surface,
        roof_perimeter_m=roof_perimeter,
        insulation_area_m2=insulation_area,
        plaster_area_m2=plaster_area,
        gutter_length_m=roof_perimeter if roof is not None else 0.0,
        railing_length_m=railing_length,
        timber_or_roof_element_count=timber_or_roof_count,
        room_count=sum(item.room_count for item in levels),
        levels=levels,
    )


__all__ = ["LevelQuantity", "BuildingQuantityTakeoff", "calculate_quantity_takeoff"]
