"""Read-only scientific views over the production GUI BuildingModel.

The canonical physical model is ``lat_ces.building.model.BuildingModel``.
Scientific modules project immutable views from that object; they do not own
rooms, walls or materials of their own.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WallView:
    wall_id: str
    product_id: str
    room_ids: tuple[str, ...]
    thickness_m: float
    exterior: bool
    load_bearing: bool
    length_m: float
    height_m: float


@dataclass(frozen=True)
class MaterialView:
    product_id: str
    manufacturer: str | None
    name: str
    dimensions_m: tuple[float, ...]
    thermal_conductivity_w_mk: float | None
    density_kg_m3: float | None
    compressive_strength_mpa: float | None


@dataclass(frozen=True)
class RoomView:
    room_id: str
    name: str
    floor_area_m2: float
    volume_m3: float
    height_m: float


@dataclass(frozen=True)
class OpeningView:
    opening_id: str
    wall_id: str
    kind: str
    width_m: float
    height_m: float


@dataclass(frozen=True)
class BuildingModelViews:
    """Immutable views; source objects remain owned by BuildingModel."""

    wall_views: tuple[WallView, ...]
    material_views: tuple[MaterialView, ...]
    room_views: tuple[RoomView, ...]
    opening_views: tuple[OpeningView, ...]

    def wall(self, wall_id: str) -> WallView:
        return next(view for view in self.wall_views if view.wall_id == wall_id)

    def material(self, product_id: str) -> MaterialView:
        return next(view for view in self.material_views if view.product_id == product_id)

    def room(self, room_id: str) -> RoomView:
        return next(view for view in self.room_views if view.room_id == room_id)


def _materials(model: Any) -> dict[str, Any]:
    return {material.material_id: material for material in model.materials.values()}


def build_read_only_views(model: Any) -> BuildingModelViews:
    """Project the production ``BuildingModel`` without creating domain copies."""
    materials = _materials(model)
    material_views = tuple(
        MaterialView(
            product_id=material.resolved_product_id,
            manufacturer=material.manufacturer,
            name=material.name,
            dimensions_m=tuple(material.dimensions_m),
            thermal_conductivity_w_mk=material.thermal_conductivity,
            density_kg_m3=material.density,
            compressive_strength_mpa=material.compressive_strength_mpa,
        )
        for material in model.materials.values()
    )

    room_views: list[RoomView] = []
    wall_views: list[WallView] = []
    opening_views: list[OpeningView] = []
    for level in model.levels.values():
        for room in level.rooms.values():
            room_views.append(RoomView(room.room_id, room.name, room.floor_area, room.volume, level.height))
        if level.floor_plan is None:
            continue
        for wall in level.floor_plan.walls.values():
            material = materials.get(wall.material_id) if wall.material_id else None
            product_id = material.resolved_product_id if material else "UNSPECIFIED"
            wall_views.append(
                WallView(
                    wall_id=wall.wall_id,
                    product_id=product_id,
                    room_ids=tuple(wall.room_ids),
                    thickness_m=wall.thickness,
                    exterior=wall.exterior,
                    load_bearing=wall.load_bearing,
                    length_m=wall.segment.length,
                    height_m=level.height,
                )
            )
            for opening in wall.openings:
                opening_views.append(
                    OpeningView(
                        opening_id=opening.opening_id,
                        wall_id=wall.wall_id,
                        kind=opening.kind,
                        width_m=opening.width,
                        height_m=opening.height_m,
                    )
                )

    return BuildingModelViews(
        wall_views=tuple(wall_views),
        material_views=material_views,
        room_views=tuple(room_views),
        opening_views=tuple(opening_views),
    )
