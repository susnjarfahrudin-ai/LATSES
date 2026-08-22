import pytest

from lat_ces.building.electrical import ElectricalLoad, calculate_electrical_report, ensure_electrical_registry
from lat_ces.building.engineering_report import build_building_engineering_report
from lat_ces.building.floor_plan import FloorPlan, Opening, Point2D, Segment2D, Wall
from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.building.model import BuildingModel, Level, Material, Roof, Room
from lat_ces.building.quantity_takeoff import calculate_quantity_takeoff
from lat_ces.building.thermal import calculate_envelope_thermal


def _model() -> BuildingModel:
    model = BuildingModel("Engineering completion")
    insulation = Material("EPS", density=20, thermal_conductivity=0.035)
    plaster = Material("Gips", density=900, thermal_conductivity=0.25)
    model.add_material(insulation)
    model.add_material(plaster)

    plan = FloorPlan("P")
    wall = Wall("W1", Segment2D(Point2D(0, 0), Point2D(5, 0)), 0.20)
    wall.add_opening(Opening(kind="window", offset=1.0, width=1.20, height_m=1.40))
    plan.add_wall(wall)
    level = Level(
        "Prizemlje", 0.0, 2.8,
        floor_plan=plan,
        length_m=5.0,
        width_m=4.0,
        insulation_material="EPS",
        insulation_thickness_m=0.16,
        interior_plaster_material="Gips",
        interior_plaster_thickness_m=0.015,
        dead_load_kpa=1.0,
        live_load_kpa=2.0,
    )
    level.add_room(Room("Soba", Box3D(Point3D(0, 0, 0), 5.0, 4.0, 2.8)))
    model.add_level(level)
    model.set_roof(Roof(roof_type="dvovodni", length_m=5.0, width_m=4.0, slope_deg=30.0, dead_load_kpa=0.5, snow_load_kpa=1.0))
    return model


def test_quantity_takeoff_includes_roof_and_openings():
    qto = calculate_quantity_takeoff(_model())
    assert qto.floor_area_m2 == pytest.approx(20.0)
    assert qto.opening_area_m2 == pytest.approx(1.68)
    assert qto.roof_plan_area_m2 == pytest.approx(20.0)
    assert qto.roof_surface_area_m2 > qto.roof_plan_area_m2
    assert qto.gutter_length_m == pytest.approx(18.0)
    assert qto.insulation_area_m2 == pytest.approx(12.32)


def test_envelope_thermal_never_invents_missing_lambda():
    model = _model()
    report = calculate_envelope_thermal(model, design_delta_t_k=25.0)
    assert report.status == "CALCULATED"
    assert report.effective_u_w_m2k is not None
    assert report.transmission_heat_loss_w is not None


def test_electrical_report_is_explicit():
    model = _model()
    registry = ensure_electrical_registry(model)
    registry.add(ElectricalLoad("Dnevna rasvjeta", "lighting", power_w=12, quantity=8, demand_factor=0.8))
    registry.add(ElectricalLoad("Utičnice", "socket", power_w=200, quantity=6, demand_factor=0.4))
    report = calculate_electrical_report(model)
    assert report.status == "CALCULATED"
    assert report.connected_power_w == pytest.approx(1296.0)
    assert report.demand_power_w == pytest.approx(556.8)


def test_unified_report_aggregates_all_domains():
    model = _model()
    registry = ensure_electrical_registry(model)
    registry.add(ElectricalLoad("Rasvjeta", "lighting", power_w=10, quantity=4, demand_factor=1.0))
    report = build_building_engineering_report(model)
    assert report.quantities.roof_surface_area_m2 > 20.0
    assert report.thermal.effective_u_w_m2k is not None
    assert report.electrical.load_count == 1
    assert report.results == ()
