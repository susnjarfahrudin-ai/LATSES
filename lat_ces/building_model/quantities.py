"""Read-only quantity/take-off views over the production BuildingModel."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


_QUANTITY_DIGITS = 12


def _q(value: float) -> float:
    return round(value, _QUANTITY_DIGITS)


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


def _product_id(model: Any, material_id: str | None) -> str | None:
    if not material_id:
        return None
    material = model.materials.get(material_id)
    return material.resolved_product_id if material else None


def to_quantity_view(model: Any) -> BuildingQuantityView:
    """Calculate quantities directly from the production GUI BuildingModel."""
    rooms: list[RoomQuantityView] = []
    walls: list[WallQuantityView] = []
    openings: list[OpeningQuantityView] = []
    stairs: list[StairQuantityView] = []
    terraces: list[TerraceQuantityView] = []

    for level in model.levels.values():
        for room in level.rooms.values():
            rooms.append(RoomQuantityView(room.room_id, room.name, _q(room.floor_area), _q(room.volume)))

        floor_plan = level.floor_plan
        if floor_plan is not None:
            for wall in floor_plan.walls.values():
                gross_area = wall.segment.length * level.height
                opening_area = sum(opening.width * opening.height_m for opening in wall.openings)
                net_area = max(gross_area - opening_area, 0.0)
                walls.append(
                    WallQuantityView(
                        wall.wall_id,
                        _product_id(model, wall.material_id),
                        _q(gross_area),
                        _q(opening_area),
                        _q(net_area),
                        _q(net_area * wall.thickness),
                    )
                )
                for opening in wall.openings:
                    openings.append(
                        OpeningQuantityView(
                            wall.wall_id,
                            opening.kind,
                            _q(opening.width * opening.height_m),
                        )
                    )

        for stair in level.stairs.values():
            stairs.append(
                StairQuantityView(
                    getattr(stair, "id"),
                    _q(float(getattr(stair, "length_m")) * float(getattr(stair, "width_m"))),
                    getattr(stair, "riser_count", None),
                )
            )

        for terrace in level.terraces.values():
            terraces.append(
                TerraceQuantityView(
                    getattr(terrace, "id"),
                    _product_id(model, getattr(getattr(terrace, "material", None), "material_id", None)),
                    _q(float(getattr(terrace, "length_m")) * float(getattr(terrace, "width_m"))),
                )
            )

    return BuildingQuantityView(
        tuple(rooms), tuple(walls), tuple(openings), tuple(stairs), tuple(terraces)
    )
