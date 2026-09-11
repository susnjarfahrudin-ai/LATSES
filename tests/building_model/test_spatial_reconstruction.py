from math import isclose

from lat_ces.adapters import adapt_building
from lat_ces.building.floor_plan import FloorPlan, Opening, Point2D, Segment2D, Wall
from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.building.model import BuildingModel, Level, Room


def minimal_spatial_house() -> BuildingModel:
    model = BuildingModel(name="Spatial Sufficiency House")
    level = Level(
        "Ground floor",
        0.0,
        2.8,
        length_m=10.0,
        width_m=8.0,
        floor_plan=FloorPlan("Ground floor plan"),
    )
    level.add_room(
        Room("Living room", Box3D(Point3D(0.0, 0.0, 0.0), 6.0, 5.0, 2.8))
    )
    level.add_room(
        Room("Kitchen", Box3D(Point3D(6.0, 0.0, 0.0), 4.0, 3.0, 2.8))
    )
    level.add_room(
        Room("Bedroom", Box3D(Point3D(0.0, 5.0, 0.0), 4.0, 3.0, 2.8))
    )

    walls = [
        Wall(
            "W1",
            Segment2D(Point2D(0.0, 0.0), Point2D(10.0, 0.0)),
            thickness=0.25,
            exterior=True,
            load_bearing=True,
        ),
        Wall(
            "W2",
            Segment2D(Point2D(10.0, 0.0), Point2D(10.0, 8.0)),
            thickness=0.25,
            exterior=True,
            load_bearing=True,
        ),
        Wall(
            "W3",
            Segment2D(Point2D(10.0, 8.0), Point2D(0.0, 8.0)),
            thickness=0.25,
            exterior=True,
            load_bearing=True,
        ),
        Wall(
            "W4",
            Segment2D(Point2D(0.0, 8.0), Point2D(0.0, 0.0)),
            thickness=0.25,
            exterior=True,
            load_bearing=True,
        ),
        Wall(
            "W5",
            Segment2D(Point2D(6.0, 0.0), Point2D(6.0, 5.0)),
            thickness=0.20,
            load_bearing=False,
        ),
    ]
    walls[0].add_opening(Opening("window", 2.0, 1.5, 2.0))
    for wall in walls:
        level.floor_plan.add_wall(wall)
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
    assert opening["height_m"] == 2.0


def test_spatial_representation_is_minimal_but_not_renderer_specific():
    scene = adapt_building(minimal_spatial_house())
    for wall in scene["levels"][0]["walls"]:
        placement = wall["placement"]
        assert set(placement) == {"x1_m", "y1_m", "x2_m", "y2_m"}
        assert "rotation_deg" not in wall
        assert "freecad" not in wall
        assert "blender" not in wall
        assert "godot" not in wall


def test_canonical_wall_length_is_derived_from_authoritative_segment():
    model = minimal_spatial_house()
    level = next(iter(model.levels.values()))
    wall = next(iter(level.floor_plan.walls.values()))
    wall.segment = Segment2D(Point2D(0.0, 0.0), Point2D(9.0, 0.0))

    scene = adapt_building(model)

    assert scene["levels"][0]["walls"][0]["length_m"] == 9.0


def test_adversarial_orientation_change_changes_authoritative_scene():
    baseline = minimal_spatial_house()
    changed = minimal_spatial_house()
    level = next(iter(changed.levels.values()))
    changed_wall = next(iter(level.floor_plan.walls.values()))
    changed_wall.segment = Segment2D(Point2D(0.0, 0.0), Point2D(0.0, 10.0))

    baseline_scene = adapt_building(baseline)
    changed_scene = adapt_building(changed)

    assert baseline_scene["levels"][0]["walls"][0]["placement"] != changed_scene["levels"][0]["walls"][0]["placement"]
