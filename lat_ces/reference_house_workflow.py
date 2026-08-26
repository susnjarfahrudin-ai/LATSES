"""Canonical Reference House -> production BuildingModel fixture.

The fixture uses the authoritative Reference House JSON for room names,
areas and heights, then constructs deterministic canonical Room and Opening
objects owned by the same BuildingModel used by the GUI and scientific views.
"""
from __future__ import annotations

from lat_ces.building.model import BuildingModel, Level, Material, Roof, Room
from lat_ces.building.workflow import BuildingWorkflow, make_envelope_floor_plan
from lat_ces.building.floor_plan import Opening, Segment2D, Point2D, Wall
from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.reference_house import ReferenceHouse


ROOM_STRIP_WIDTH_M = 10.0
WALL_THICKNESS_M = 0.25


def _add_authoritative_rooms(model: BuildingModel, level: Level, room_specs: list[dict]) -> list[Room]:
    """Create deterministic area-preserving strip footprints from fixture data."""
    rooms: list[Room] = []
    x = 0.0
    for spec in room_specs:
        height_m = float(spec["height_m"])
        if height_m <= 0.0:
            continue
        area_m2 = float(spec["area_m2"])
        length_m = area_m2 / ROOM_STRIP_WIDTH_M
        room = Room(
            name=str(spec["name"]),
            footprint=Box3D(
                origin=Point3D(x, 0.0, level.elevation),
                length=length_m,
                width=ROOM_STRIP_WIDTH_M,
                height=height_m,
            ),
        )
        level.add_room(room)
        rooms.append(room)
        x += length_m
    return rooms


def _add_internal_partition_walls(level: Level, rooms: list[Room], material_id: str, load_bearing: bool) -> None:
    if not level.floor_plan or len(rooms) < 2:
        return
    for previous, current in zip(rooms, rooms[1:]):
        x = current.footprint.origin.x
        tributary_width_m = (previous.footprint.length + current.footprint.length) / 2.0
        wall = Wall(
            name=f"Pregrada {previous.name} / {current.name}",
            segment=Segment2D(Point2D(x, 0.0), Point2D(x, ROOM_STRIP_WIDTH_M)),
            thickness=WALL_THICKNESS_M,
            load_bearing=load_bearing,
            material_id=material_id,
            tributary_width_m=tributary_width_m if load_bearing else 0.0,
            exterior=False,
            room_ids=(previous.room_id, current.room_id),
        )
        level.floor_plan.add_wall(wall)


def _add_deterministic_openings(level: Level) -> None:
    if not level.floor_plan:
        return
    walls = sorted(level.floor_plan.walls.values(), key=lambda wall: (-wall.segment.length, wall.wall_id))
    if not walls:
        return
    door_wall = walls[0]
    door_width = min(0.90, door_wall.segment.length * 0.25)
    door_offset = max(0.10, (door_wall.segment.length - door_width) / 2.0)
    door_wall.add_opening(Opening(kind="door", offset=door_offset, width=door_width, height_m=2.10))
    for window_wall in walls[1:3]:
        window_width = min(1.20, window_wall.segment.length * 0.30)
        offset = max(0.10, (window_wall.segment.length - window_width) / 2.0)
        window_wall.add_opening(Opening(kind="window", offset=offset, width=window_width, height_m=1.50))


def build_reference_house_workflow() -> BuildingWorkflow:
    house = ReferenceHouse.default()
    dimensions = house.data["dimensions"]
    length_m = float(dimensions["length_m"])
    width_m = float(dimensions["width_m"])
    height_m = float(dimensions["level_height_m"])

    model = BuildingModel(name=house.data["name"])
    masonry = Material(
        name=str(house.data["envelope"]["exterior_wall"]["masonry_block"]),
        dimensions_m=(0.25, 0.20, 0.25),
        product_id="CATALOG:masonry_block:250x200x250",
        category="masonry_block",
    )
    model.add_material(masonry)

    for index, level_data in enumerate(house.levels):
        loads = level_data.get("loads", {})
        level = Level(
            name=level_data["name"],
            elevation=index * height_m,
            height=height_m,
            length_m=length_m,
            width_m=width_m,
            dead_load_kpa=float(loads.get("dead_kpa", 0.0)),
            live_load_kpa=float(loads.get("live_kpa", 0.0)),
        )
        level.set_floor_plan(make_envelope_floor_plan(level.name, length_m, width_m, WALL_THICKNESS_M))
        rooms = _add_authoritative_rooms(model, level, level_data.get("rooms", []))
        if level.floor_plan:
            for wall in level.floor_plan.walls.values():
                wall.material_id = masonry.material_id
                wall.load_bearing = model.load_bearing_mode == "all_walls" or wall.exterior
                if wall.load_bearing and wall.tributary_width_m <= 0.0:
                    wall.tributary_width_m = width_m / 2.0
            _add_internal_partition_walls(level, rooms, masonry.material_id, model.load_bearing_mode == "all_walls")
            _add_deterministic_openings(level)
        model.add_level(level)

    roof_data = house.data.get("roof", {})
    model.set_roof(
        Roof(
            roof_type=str(roof_data.get("type", "dvovodni")),
            covering=str(roof_data.get("covering", "")),
            length_m=length_m,
            width_m=width_m,
            slope_deg=float(roof_data.get("slope_deg", 0.0)),
            height_m=0.0,
        )
    )

    return BuildingWorkflow(
        model=model,
        current_step=3,
        active_level_id=next(iter(model.levels), None),
    )


__all__ = ["build_reference_house_workflow"]
