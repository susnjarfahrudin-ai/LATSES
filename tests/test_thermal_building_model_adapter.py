from lat_ces.building.floor_plan import FloorPlan, Point2D, Segment2D, Wall
from lat_ces.building.model import BuildingModel, Level, Material
from lat_ces.thermal import to_thermal_input


def _model():
    material = Material("Thermo Block 25", thermal_conductivity=.18, product_id="product:block-25", manufacturer="Example")
    model = BuildingModel("Reference House")
    model.add_material(material)
    level = Level("Ground", 0.0, 2.70, length_m=10.0, width_m=10.0)
    plan = FloorPlan("Ground")
    plan.add_wall(Wall("Exterior", Segment2D(Point2D(0, 0), Point2D(4, 0)), .25, "wall-001", material_id=material.material_id, exterior=True, room_ids=("room-kitchen",)))
    level.set_floor_plan(plan)
    model.add_level(level)
    return model


def test_thermal_uses_production_product_and_wall_identity():
    thermal = to_thermal_input(_model())
    assert thermal.walls[0].wall_id == "wall-001"
    assert thermal.walls[0].product_id == "product:block-25"
    assert thermal.walls[0].thermal_conductivity_w_mk == .18
    assert thermal.walls[0].conductive_resistance_m2kw == .25 / .18
