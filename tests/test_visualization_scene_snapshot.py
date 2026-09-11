"""Verification of the canonical BuildingModel -> scene.v1 snapshot boundary."""

from lat_ces.adapters import adapt_building, adapt_scene_2d, adapt_scene_3d
from lat_ces.building.floor_plan import FloorPlan, Point2D, Segment2D, Wall
from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.building.model import BuildingModel, Level, Room


def _model() -> BuildingModel:
    model = BuildingModel(name="Snapshot House")
    level = Level(
        name="Ground",
        elevation=0.0,
        height=3.0,
        level_id="ground",
        length_m=10.0,
        width_m=8.0,
        floor_plan=FloorPlan(name="Ground Plan"),
    )
    level.add_room(
        Room(
            name="Living",
            room_id="living",
            footprint=Box3D(
                origin=Point3D(0.0, 0.0, 0.0),
                length=5.0,
                width=4.0,
                height=3.0,
            ),
        )
    )
    level.floor_plan.add_wall(
        Wall(
            name="South",
            wall_id="south",
            segment=Segment2D(Point2D(0.0, 0.0), Point2D(10.0, 0.0)),
            thickness=0.30,
            exterior=True,
        )
    )
    model.add_level(level)
    return model


def test_one_scene_snapshot_feeds_both_2d_and_3d_consumers() -> None:
    model = _model()
    scene = adapt_building(model)
    scene_2d = adapt_scene_2d(scene)
    scene_3d = adapt_scene_3d(scene)

    assert scene["schema"] == "latces.visualization.scene.v1"
    assert scene_2d["source_schema"] == scene["schema"]
    assert scene_3d["source_schema"] == scene["schema"]
    assert scene_2d["source"] == scene["source"]
    assert scene_3d["source"] == scene["source"]

    wall_2d = scene_2d["levels"][0]["walls"][0]
    wall_3d = scene_3d["levels"][0]["walls"][0]
    assert wall_2d["id"] == wall_3d["id"] == "south"
    assert [wall_2d["x1_m"], wall_2d["y1_m"]] == wall_3d["start_m"][:2]
    assert [wall_2d["x2_m"], wall_2d["y2_m"] == wall_3d["end_m"][:2]
    assert wall_2d["thickness_m"] == wall_3d["thickness_m"] == 0.30


def test_building_change_requires_a_new_scene_snapshot() -> None:
    model = _model()
    first_scene = adapt_building(model)

    wall = model.levels["ground"].floor_plan.walls["south"]
    wall.segment = Segment2D(Point2D(0.0, 0.0), Point2D(12.0, 0.0))
    second_scene = adapt_building(model)

    assert first_scene["levels"][0]["walls"][0]["length_m"] == 10.0
    assert first_scene["levels"][0]["walls"][0]["placement"]["x2_m"] == 10.0
    assert second_scene["levels"][0]["walls"][0]["length_m"] == 12.0
    assert second_scene["levels"][0]["walls"][0]["placement"]["x2_m"] == 12.0
    assert first_scene != second_scene
