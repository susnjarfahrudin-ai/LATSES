"""Verification of the canonical BuildingModel -> scene.v1 snapshot boundary."""

from lat_ces.adapters import adapt_building, adapt_scene_2d, adapt_scene_3d
from lat_ces.building_model import BuildingModel, Level, Room, Wall, WallPlacement


def _model() -> BuildingModel:
    model = BuildingModel(name="Snapshot House")
    level = Level(id="ground", name="Ground", length_m=10.0, width_m=8.0, height_m=3.0)
    level.add_room(Room("living", "Living", 5.0, 4.0, 3.0))
    level.add_wall(
        Wall(
            id="south",
            length_m=10.0,
            thickness_m=0.30,
            height_m=3.0,
            exterior=True,
            placement=WallPlacement(0.0, 0.0, 10.0, 0.0),
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
    assert [wall_2d["x2_m"], wall_2d["y2_m"]] == wall_3d["end_m"][:2]
    assert wall_2d["thickness_m"] == wall_3d["thickness_m"] == 0.30


def test_building_change_requires_a_new_scene_snapshot() -> None:
    model = _model()
    first_scene = adapt_building(model)

    wall = model.levels["ground"].walls["south"]
    wall.length_m = 12.0
    wall.placement = WallPlacement(0.0, 0.0, 12.0, 0.0)
    second_scene = adapt_building(model)

    assert first_scene["levels"][0]["walls"][0]["length_m"] == 10.0
    assert first_scene["levels"][0]["walls"][0]["placement"]["x2_m"] == 10.0
    assert second_scene["levels"][0]["walls"][0]["length_m"] == 12.0
    assert second_scene["levels"][0]["walls"][0]["placement"]["x2_m"] == 12.0
    assert first_scene != second_scene
