"""Geometry-driven quantity take-off from the canonical BuildingModel."""
from __future__ import annotations

from dataclasses import dataclass

from .model import BuildingModel


@dataclass(frozen=True)
class LevelQuantity:
    level_id: str
    name: str
    floor_area_m2: float
    volume_m3: float
    wall_length_m: float
    room_count: int


@dataclass(frozen=True)
class BuildingQuantityTakeoff:
    floor_area_m2: float
    volume_m3: float
    wall_length_m: float
    roof_plan_area_m2: float
    room_count: int
    levels: tuple[LevelQuantity, ...]


def _level_quantity(level) -> LevelQuantity:
    plan = level.floor_plan
    wall_length = 0.0 if plan is None else sum(wall.segment.length for wall in plan.walls.values())
    return LevelQuantity(
        level_id=level.level_id,
        name=level.name,
        floor_area_m2=level.floor_area,
        volume_m3=level.volume,
        wall_length_m=wall_length,
        room_count=len(level.rooms),
    )


def calculate_quantity_takeoff(model: BuildingModel) -> BuildingQuantityTakeoff:
    """Calculate quantities only from geometry/state already present in model."""
    levels = tuple(_level_quantity(level) for level in model.levels.values())
    roof_area = model.roof.plan_area_m2 if model.roof is not None else 0.0
    return BuildingQuantityTakeoff(
        floor_area_m2=sum(item.floor_area_m2 for item in levels),
        volume_m3=sum(item.volume_m3 for item in levels),
        wall_length_m=sum(item.wall_length_m for item in levels),
        roof_plan_area_m2=roof_area,
        room_count=sum(item.room_count for item in levels),
        levels=levels,
    )


__all__ = ["LevelQuantity", "BuildingQuantityTakeoff", "calculate_quantity_takeoff"]
