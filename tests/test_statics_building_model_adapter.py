from lat_ces.building.floor_plan import FloorPlan, Point2D, Segment2D, Wall
from lat_ces.building.model import BuildingModel, Level, Material
from lat_ces.structural.building_model_adapter import to_static_input


def _model():
    material = Material("Thermo Block 25", density=800.0, compressive_strength_mpa=10.0, product_id="product:block-25", manufacturer="Example")
    model = BuildingModel("Reference House")
    model.add_material(material)
    level = Level("Ground", 0.0, 2.70, length_m=10.0, width_m=10.0)
    plan = FloorPlan("Ground")
    plan.add_wall(Wall("Exterior", Segment2D(Point2D(0, 0), Point2D(4, 0)), .25, "wall-001", material_id=material.material_id, load_bearing=True, exterior=True, room_ids=("room-kitchen",)))
    level.set_floor_plan(plan)
    model.add_level(level)
    return model


def test_production_model_feeds_statics_without_duplicate_wall_identity():
    model = _model()
    static = to_static_input(model)
    assert {wall.wall_id for wall in static.walls} == {"wall-001"}
    assert static.walls[0].product_id == "product:block-25"
    assert static.walls[0].density_kg_m3 == 800.0
    assert static.walls[0].compressive_strength_mpa == 10.0
    assert static.walls[0].thickness_m == .25
