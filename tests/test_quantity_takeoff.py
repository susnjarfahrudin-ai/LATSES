import pytest

from lat_ces.building.floor_plan import FloorPlan, Point2D, Segment2D, Wall
from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.building.model import BuildingModel, Level, Roof, Room
from lat_ces.building.quantity_takeoff import calculate_quantity_takeoff


def test_quantity_takeoff_uses_canonical_geometry():
    model = BuildingModel("QTO test")
    plan = FloorPlan("P")
    plan.add_wall(Wall("W1", Segment2D(Point2D(0, 0), Point2D(4, 0)), 0.2))
    level = Level(
        "Prizemlje",
        elevation=0.0,
        height=2.8,
        floor_plan=plan,
        length_m=4.0,
        width_m=3.0,
    )
    level.add_room(Room("Soba", Box3D(Point3D(0, 0, 0), 4.0, 3.0, 2.8)))
    model.add_level(level)
    model.set_roof(Roof(roof_type="dvovodni", length_m=4.0, width_m=3.0))

    qto = calculate_quantity_takeoff(model)

    assert qto.floor_area_m2 == pytest.approx(12.0)
    assert qto.volume_m3 == pytest.approx(33.6)
    assert qto.wall_length_m == pytest.approx(4.0)
    assert qto.roof_plan_area_m2 == pytest.approx(12.0)
    assert qto.room_count == 1
    assert qto.levels[0].room_count == 1
