from math import isclose

import pytest

from lat_ces.adapters import adapt_building
from lat_ces.building_model import BuildingModel, Level, Opening, Room, Wall, WallPlacement


def minimal_spatial_house() -> BuildingModel:
    model = BuildingModel(name="Spatial Sufficiency House")
    level = Level("L1", "Ground floor", 10.0, 8.0, 2.8)
    level.add_room(Room("R1", "Living room", 6.0, 5.0, 2.8))
    level.add_room(Room("R2", "Kitchen", 4.0, 3.0, 2.8))
    level.add_room(Room("R3", "Bedroom", 4.0, 3.0, 2.8))

    walls = [
        Wall("W1", 10.0, 0.25, 2.8, exterior=True, load_bearing=True,
             placement=WallPlacement(0.0, 0.0, 10.0, 0.0)),
        Wall("W2", 8.0, 0.25, 2.8, exterior=True, load_bearing=True,
             placement=WallPlacement(10.0, 0.0, 10.0, 8.0)),
        Wall("W3", 8.0, 0.25, 2.8, exterior=True, load_bearing=True,
             placement=WallPlacement(10.0, 8.0, 0.0, 8.0)),
        Wall("W4", 8.0, 0.25, 2.8, exterior=True, load_bearing=True,
             placement=WallPlacement(0.0, 8.0, 0.0, 0.0)),
        Wall("W5", 5.0, 0.20, 2.8, load_bearing=False,
             placement=WallPlacement(6.0, 0.0, 6.0, 5.0)),
    ]
    walls[0].add_opening(Opening("window", 1.5, 1.2, 0.9, 2.0))
    for wall in walls:
        level.add_wall(wall)
    model.add_level(level)
    return model


def test_minimal_house_has_reconstructable_authoritative_wall_geometry():
    scene = adapt_building(minimal_spatial_house())
    level = scene["levels"][0]
    walls = level["walls"]

    assert len(walls) == 5
    assert all("placement" in wall for wall in walls)

    exterior = [walls[i]["placement"] for i in range(4)]
    assert exterior[0] == {"x1_m": 0.0, "y1_m": 0.0, "x2_m": 10.0, "y2_m": 0.0}
    assert exterior[1] == {"x1_m": 10.0, "y1_m": 0.0, "x2_m": 10.0, "y2_m": 8.0}
    assert exterior[2] == {"x1_m": 10.0, "y1_m": 8.0, "x2_m": 0.0, "y2_m": 8.0}
    assert exterior[3] == {"x1_m": 0.0, "y1_m": 8.0, "x2_m": 0.0, "y2_m": 0.0}

    lengths = []
    for wall in walls:
        p = wall["placement"]
        lengths.append(((p["x2_m"] - p["x1_m"]) ** 2 +
                        (p["y2_m"] - p["y1_m"]) ** 2) ** 0.5)
    assert all(isclose(lengths[i], walls[i]["length_m"], abs_tol=1e-9) for i in range(5))

    opening = walls[0]["openings"][0]
    assert opening["position_m"] == 2.0
    assert opening["width_m"] == 1.5
    assert opening["sill_height_m"] == 0.9


def test_spatial_representation_is_minimal_but_not_renderer_specific():
    scene = adapt_building(minimal_spatial_house())
    for wall in scene["levels"][0]["walls"]:
        placement = wall["placement"]
        assert set(placement) == {"x1_m", "y1_m", "x2_m", "y2_m"}
        assert "rotation_deg" not in wall
        assert "freecad" not in wall
        assert "blender" not in wall
        assert "godot" not in wall


def test_wall_length_and_placement_cannot_disagree():
    with pytest.raises(ValueError, match="placement length"):
        Wall(
            "bad",
            10.0,
            0.25,
            2.8,
            placement=WallPlacement(0.0, 0.0, 9.0, 0.0),
        )


def test_adversarial_orientation_change_changes_authoritative_scene():
    baseline = minimal_spatial_house()
    changed = minimal_spatial_house()
    changed.levels["L1"].walls["W1"].placement = WallPlacement(0.0, 0.0, 0.0, 10.0)

    baseline_scene = adapt_building(baseline)
    changed_scene = adapt_building(changed)

    assert baseline_scene["levels"][0]["walls"][0]["placement"] != changed_scene["levels"][0]["walls"][0]["placement"]
