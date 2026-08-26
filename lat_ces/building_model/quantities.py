"""Read-only quantity/take-off views over the canonical Building Model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RoomQuantityView:
    room_id: str
    name: str
    floor_area_m2: float
    volume_m3: float


@dataclass(frozen=True)
class WallQuantityView:
    wall_id: str
    product_id: str | None
    gross_area_m2: float
    opening_area_m2: float
    net_area_m2: float
    volume_m3: float


@dataclass(frozen=True)
class OpeningQuantityView:
    wall_id: str
    kind: str
    area_m2: float


@dataclass(frozen=True)
class StairQuantityView:
    stair_id: str
    plan_area_m2: float
    riser_count: int | None


@dataclass(frozen=True)
class TerraceQuantityView:
    terrace_id: str
    product_id: str | None
    area_m2: float


@dataclass(frozen=True)
class BuildingQuantityView:
    rooms: tuple[RoomQuantityView, ...]
    walls: tuple[WallQuantityView, ...]
    openings: tuple[OpeningQuantityView, ...]
    stairs: tuple[StairQuantityView, ...]
    terraces: tuple[TerraceQuantityView, ...]


def to_quantity_view(model: Any) -> BuildingQuantityView:
    """Calculate quantities directly from canonical BuildingModel objects."""
    room_views: list[RoomQuantityView] = []
    wall_views: list[WallQuantityView] = []
    opening_views: list[OpeningQuantityView] = []
    stair_views: list[StairQuantityView] = []
    terrace_views: list[TerraceQuantityView] = []

    for level in model.levels.values():
        for room in level.rooms.values():
            height = room.resolve_height(level.height_m)
            room_views.append(
                RoomQuantityView(room.id, room.name, room.length_m * room.width_m, room.length_m * room.width_m * height)
            )
        for wall in level.walls.values():
            gross_area = wall.length_m * wall.height_m
            opening_area = sum(opening.width_m * opening.height_m for opening in wall.openings)
            net_area = max(gross_area - opening_area, 0.0)
            wall_views.append(
                WallQuantityView(
                    wall.id,
                    wall.material.product_id if wall.material else None,
                    gross_area,
                    opening_area,
                    net_area,
                    net_area * wall.thickness_m,
                )
            )
            for opening in wall.openings:
                opening_views.append(
                    OpeningQuantityView(wall.id, opening.kind, opening.width_m * opening.height_m)
                )
        for stair in level.stairs.values():
            stair_views.append(StairQuantityView(stair.id, stair.length_m * stair.width_m, stair.riser_count))
        for terrace in level.terraces.values():
            terrace_views.append(
                TerraceQuantityView(
                    terrace.id,
                    terrace.material.product_id if terrace.material else None,
                    terrace.length_m * terrace.width_m,
                )
            )

    return BuildingQuantityView(
        tuple(room_views), tuple(wall_views), tuple(opening_views), tuple(stair_views), tuple(terrace_views)
    )
