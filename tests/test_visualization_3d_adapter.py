from dataclasses import FrozenInstanceError

from lat_ces.building.floor_plan import FloorPlan, Opening, Point2D, Segment2D, Wall
from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.building.model import BuildingModel, Level, Room
from lat_ces.visualization_3d_adapter import BuildingScene3D, to_building_scene_3d


def make_model() -> BuildingModel:
    model = BuildingModel("3D Test Building", model_id="BM-3D-001")
    level = Level("Ground", elevation=2.0, height=3.0, level_id="LVL-001")
    room = Room(
        "Living",
        Box3D(Point3D(1.0, 2.0, 0.0), 5.0, 4.0, 3.0),
        room_id="ROOM-001",
    )
    level.add_room(room)

    plan = FloorPlan("Ground plan", plan_id="PLAN-001")
    wall = Wall(
        "North wall",
        Segment2D(Point2D(0.0, 0.0), Point2D(6.0, 0.0)),
        thickness=0.2,
        wall_id="WALL-001",
        exterior=True,
        room_ids=(room.room_id,),
    )
    wall.add_opening(Opening("window", offset=1.5, width=1.2, height_m=1.4, opening_id="OPN-001"))
    plan.add_wall(wall)
    level.set_floor_plan(plan)
    model.add_level(level)
    return model


def test_projection_preserves_canonical_building_identity() -> None:
    model = make_model()
    before = model
    scene = to_building_scene_3d(model)

    assert isinstance(scene, BuildingScene3D)
    assert scene.building_model_id == model.model_id
    assert scene.source_ref == "building-model:BM-3D-001"
    assert model is before


def test_projection_contains_room_wall_and_opening_geometry() -> None:
    scene = to_building_scene_3d(make_model())

    assert [item.element_type for item in scene.objects] == ["room", "wall", "opening"]

    room, wall, opening = scene.objects
    assert room.source_element_id == "ROOM-001"
    assert room.geometry.origin_x_m == 1.0
    assert room.geometry.origin_y_m == 2.0
    assert room.geometry.origin_z_m == 2.0
    assert room.geometry.length_m == 5.0
    assert room.geometry.width_m == 4.0
    assert room.geometry.height_m == 3.0

    assert wall.source_element_id == "WALL-001"
    assert wall.geometry.length_m == 6.0
    assert wall.geometry.width_m == 0.2
    assert wall.geometry.height_m == 3.0
    assert wall.geometry.rotation_z_deg == 0.0

    assert opening.source_element_id == "OPN-001"
    assert opening.role == "void"
    assert opening.geometry.origin_x_m == 1.5
    assert opening.geometry.origin_y_m == 0.0
    assert opening.geometry.length_m == 1.2
    assert opening.geometry.width_m == 0.2
    assert opening.geometry.height_m == 1.4


def test_wall_geometry_follows_segment_direction() -> None:
    model = BuildingModel("Rotated Building", model_id="BM-3D-002")
    level = Level("Ground", elevation=0.0, height=3.0, level_id="LVL-002")
    plan = FloorPlan("Ground plan", plan_id="PLAN-002")
    plan.add_wall(
        Wall(
            "East wall",
            Segment2D(Point2D(2.0, 3.0), Point2D(2.0, 8.0)),
            thickness=0.25,
            wall_id="WALL-002",
        )
    )
    level.set_floor_plan(plan)
    model.add_level(level)

    scene = to_building_scene_3d(model)
    geometry = scene.objects[0].geometry

    assert geometry.origin_x_m == 2.0
    assert geometry.origin_y_m == 3.0
    assert geometry.length_m == 5.0
    assert geometry.rotation_z_deg == 90.0


def test_scene_is_immutable() -> None:
    scene = to_building_scene_3d(make_model())

    try:
        scene.building_model_id = "changed"
    except FrozenInstanceError:
        pass
    else:
        raise AssertionError("BuildingScene3D must be immutable")


def test_adapter_rejects_noncanonical_model() -> None:
    try:
        to_building_scene_3d(object())
    except TypeError as exc:
        assert "production BuildingModel" in str(exc)
    else:
        raise AssertionError("non-canonical model must be rejected")
