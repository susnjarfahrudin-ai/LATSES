from lat_ces.building.floor_plan import FloorPlan, Opening, Point2D, Segment2D, Wall
from lat_ces.building.geometry import Box3D
from lat_ces.building.model import BuildingModel, Level, Material, Room
from lat_ces.building_model.quantities import to_quantity_view


def _canonical_model():
    material = Material(
        "Thermo Block 25",
        density=800.0,
        thermal_conductivity=0.18,
        compressive_strength_mpa=10.0,
        product_id="product:block-25",
        manufacturer="Example",
        dimensions_m=(0.25, 0.25, 0.30),
    )
    model = BuildingModel("Reference House")
    model.add_material(material)
    level = Level("Ground", 0.0, 2.70, length_m=10.0, width_m=10.0)
    level.add_room(Room("Kuhinja", Box3D(0.0, 0.0, 0.0, 3.0, 3.0, 2.70), room_id="room-kitchen"))
    plan = FloorPlan("Ground")
    wall = Wall(
        "Exterior kitchen wall",
        Segment2D(Point2D(0.0, 0.0), Point2D(4.0, 0.0)),
        thickness=0.25,
        wall_id="wall-1",
        material_id=material.material_id,
        load_bearing=True,
        exterior=True,
        room_ids=("room-kitchen",),
    )
    wall.add_opening(Opening("window", 1.0, 1.2, height_m=1.2, opening_id="window-1"))
    plan.add_wall(wall)
    level.set_floor_plan(plan)
    model.add_level(level)
    return model


def test_quantities_read_production_geometry_and_product_identity():
    view = to_quantity_view(_canonical_model())

    assert view.rooms[0].room_id == "room-kitchen"
    assert view.rooms[0].name == "Kuhinja"
    assert view.rooms[0].floor_area_m2 == 9.0
    assert view.rooms[0].volume_m3 == 24.3
    assert view.walls[0].wall_id == "wall-1"
    assert view.walls[0].product_id == "product:block-25"
    assert view.walls[0].gross_area_m2 == 10.8
    assert view.walls[0].opening_area_m2 == 1.44
    assert view.walls[0].net_area_m2 == 9.36
    assert view.walls[0].volume_m3 == 2.34
    assert view.openings[0].wall_id == "wall-1"


def test_quantity_views_are_immutable():
    view = to_quantity_view(_canonical_model())
    try:
        view.rooms[0].name = "other"
    except Exception:
        pass
    else:
        raise AssertionError("quantity views must be immutable")
    assert view.rooms[0].room_id == "room-kitchen"
