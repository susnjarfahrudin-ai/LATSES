from lat_ces.building.floor_plan import FloorPlan, Point2D, Segment2D, Wall
from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.building.model import BuildingModel, Level, Material, Room
from lat_ces.building_model.source_of_truth import build_read_only_views


def _model():
    product = Material("Block 25", density=800.0, thermal_conductivity=0.18, compressive_strength_mpa=10.0, product_id="product:block-25", manufacturer="Example", dimensions_m=(.25, .25, .30))
    model = BuildingModel("Reference House")
    model.add_material(product)
    level = Level("Ground", 0.0, 2.70, length_m=10.0, width_m=10.0)
    level.add_room(Room("Kuhinja", Box3D(Point3D(0, 0, 0), 3, 3, 2.7), room_id="room-kitchen"))
    plan = FloorPlan("Ground")
    plan.add_wall(Wall("Kitchen wall", Segment2D(Point2D(0, 0), Point2D(4, 0)), .25, "wall-001", material_id=product.material_id, exterior=True, room_ids=("room-kitchen",)))
    level.set_floor_plan(plan)
    model.add_level(level)
    return model


def test_scientific_views_preserve_production_identities():
    model = _model()
    views = build_read_only_views(model)
    assert views.wall_views[0].wall_id == "wall-001"
    assert views.wall_views[0].product_id == "product:block-25"
    assert views.room_views[0].room_id == "room-kitchen"
    assert views.material_views[0].product_id == "product:block-25"


def test_scientific_views_are_immutable():
    views = build_read_only_views(_model())
    try:
        views.wall_views[0].wall_id = "different"
    except Exception:
        pass
    else:
        raise AssertionError("scientific views must be immutable")
    assert views.wall_views[0].wall_id == "wall-001"
