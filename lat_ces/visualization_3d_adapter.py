"""Read-only canonical 3-D scene projection from the production BuildingModel.

This module defines the neutral scene exchanged between LATSES and any renderer.
It contains representation geometry and canonical identity only. It does not
calculate engineering results, mutate the BuildingModel, or depend on Blender,
Geometry Nodes, ParaView, or another rendering backend.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import atan2, degrees, hypot

from lat_ces.building.model import BuildingModel


@dataclass(frozen=True)
class SceneBox3D:
    """Renderer-neutral rectangular solid/void description in SI metres."""

    origin_x_m: float
    origin_y_m: float
    origin_z_m: float
    length_m: float
    width_m: float
    height_m: float
    rotation_z_deg: float = 0.0


@dataclass(frozen=True)
class SceneObject3D:
    """Immutable visual representation linked to one canonical model element."""

    visual_object_id: str
    source_element_id: str
    element_type: str
    geometry: SceneBox3D
    role: str = "solid"
    material_ref: str | None = None
    name: str = ""


@dataclass(frozen=True)
class BuildingScene3D:
    """Immutable 3-D architectural scene projected from one BuildingModel."""

    building_model_id: str
    source_ref: str
    objects: tuple[SceneObject3D, ...]
    status: str = "READY"


def _wall_geometry(wall: object, *, elevation_m: float, height_m: float) -> SceneBox3D:
    start = wall.segment.start
    end = wall.segment.end
    dx = end.x - start.x
    dy = end.y - start.y
    length = hypot(dx, dy)
    angle = degrees(atan2(dy, dx))
    return SceneBox3D(
        origin_x_m=start.x,
        origin_y_m=start.y,
        origin_z_m=elevation_m,
        length_m=length,
        width_m=wall.thickness,
        height_m=height_m,
        rotation_z_deg=angle,
    )


def _opening_geometry(wall: object, opening: object, *, elevation_m: float) -> SceneBox3D:
    start = wall.segment.start
    end = wall.segment.end
    dx = end.x - start.x
    dy = end.y - start.y
    wall_length = hypot(dx, dy)
    ux = dx / wall_length
    uy = dy / wall_length
    offset_x = start.x + ux * opening.offset
    offset_y = start.y + uy * opening.offset
    angle = degrees(atan2(dy, dx))
    return SceneBox3D(
        origin_x_m=offset_x,
        origin_y_m=offset_y,
        origin_z_m=elevation_m,
        length_m=opening.width,
        width_m=wall.thickness,
        height_m=opening.height_m,
        rotation_z_deg=angle,
    )


def to_building_scene_3d(model: BuildingModel) -> BuildingScene3D:
    """Project canonical building geometry into an immutable renderer-neutral scene.

    The adapter reads the production ``BuildingModel`` directly because the
    existing scientific read-only views intentionally omit wall coordinates and
    level elevation. No new physical identity is created and the source model
    is never mutated.
    """
    if not isinstance(model, BuildingModel):
        raise TypeError("model must be a production BuildingModel")

    objects: list[SceneObject3D] = []
    for level in model.levels.values():
        for room in level.rooms.values():
            footprint = room.footprint
            objects.append(
                SceneObject3D(
                    visual_object_id=f"room:{room.room_id}",
                    source_element_id=room.room_id,
                    element_type="room",
                    geometry=SceneBox3D(
                        origin_x_m=footprint.origin.x,
                        origin_y_m=footprint.origin.y,
                        origin_z_m=footprint.origin.z + level.elevation,
                        length_m=footprint.length,
                        width_m=footprint.width,
                        height_m=footprint.height,
                    ),
                    role="context",
                    name=room.name,
                )
            )

        if level.floor_plan is None:
            continue

        for wall in level.floor_plan.walls.values():
            objects.append(
                SceneObject3D(
                    visual_object_id=f"wall:{wall.wall_id}",
                    source_element_id=wall.wall_id,
                    element_type="wall",
                    geometry=_wall_geometry(
                        wall,
                        elevation_m=level.elevation,
                        height_m=level.height,
                    ),
                    material_ref=wall.material_id,
                    name=wall.name,
                )
            )
            for opening in wall.openings:
                objects.append(
                    SceneObject3D(
                        visual_object_id=f"opening:{opening.opening_id}",
                        source_element_id=opening.opening_id,
                        element_type="opening",
                        geometry=_opening_geometry(
                            wall,
                            opening,
                            elevation_m=level.elevation,
                        ),
                        role="void",
                        name=opening.kind,
                    )
                )

    return BuildingScene3D(
        building_model_id=model.model_id,
        source_ref=f"building-model:{model.model_id}",
        objects=tuple(objects),
    )


__all__ = ["SceneBox3D", "SceneObject3D", "BuildingScene3D", "to_building_scene_3d"]
