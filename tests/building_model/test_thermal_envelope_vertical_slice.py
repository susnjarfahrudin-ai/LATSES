from lat_ces.building.floor_plan import FloorPlan, Point2D, Segment2D, Wall
from lat_ces.building.model import BuildingModel, Level, Material
from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.building.engineering_report import build_building_engineering_report
from lat_ces.building.thermal_envelope import calculate_wall_thermal_result


def make_model() -> tuple[BuildingModel, Level, Wall]:
    model = BuildingModel("Thermal slice")
    material = Material("Brick", thermal_conductivity=0.70, density=1800.0)
    model.add_material(material)
    level = Level("Ground", elevation=0.0, height=3.0, length_m=10.0, width_m=8.0)
    plan = FloorPlan("Ground floor")
    wall = Wall(
        "Exterior north",
        Segment2D(Point2D(0.0, 0.0), Point2D(10.0, 0.0)),
        thickness=0.20,
        material_id=material.material_id,
        exterior=True,
    )
    plan.add_wall(wall)
    level.set_floor_plan(plan)
    model.add_level(level)
    return model, level, wall


def test_thermal_slice_wall_to_u_to_q_and_validation() -> None:
    model, level, wall = make_model()
    result = calculate_wall_thermal_result(
        model,
        level,
        wall,
        indoor_temperature_c=20.0,
        outdoor_temperature_c=-10.0,
    )

    assert result.status == "CALCULATED"
    assert result.building_model_id == model.model_id
    assert result.object_id == wall.wall_id
    assert result.object_type == "thermal_wall"
    assert result.values["area_m2"] == 30.0
    assert round(result.values["u_value_w_m2k"], 6) == round(1.0 / (0.13 + 0.20 / 0.70 + 0.04), 6)
    assert round(result.values["heat_loss_w"], 6) == round(
        result.values["u_value_w_m2k"] * 30.0 * 30.0, 6
    )


def test_building_engineering_report_contains_thermal_result() -> None:
    model, _, _ = make_model()
    report = build_building_engineering_report(model)

    assert report.status == "CALCULATED"
    assert report.result_count == 1
    assert report.calculated_count == 1
    assert report.input_required_count == 0
    assert report.conflict_count == 0
    assert report.validation_failure_count == 0
    assert report.total_opaque_wall_heat_loss_w > 0.0
    assert report.results[0].building_model_id == model.model_id
