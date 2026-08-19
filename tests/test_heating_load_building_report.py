import math

from lat_ces.building.engineering_report import build_building_engineering_report
from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building.mep_engineering import MEPEngineeringService
from lat_ces.building.model import BuildingModel
from lat_ces.building_model.systems import HeatingZone, VentilationOpening, WaterBranch


def test_room_heat_load_produces_real_mass_flow():
    zone = HeatingZone("HZ-LOAD", "R1", "underfloor", 35.0, 28.0, 20.0, room_heat_load_w=10000.0)
    result = MEPEngineeringService().calculate_heating(zone)

    expected_mass_flow = 10000.0 / (4180.0 * 7.0)
    assert result.status == "CALCULATED"
    assert math.isclose(result.values["mass_flow_kg_s"], expected_mass_flow, rel_tol=1e-9)
    assert math.isclose(result.values["heat_rate_w"], 10000.0, rel_tol=1e-9)


def test_mass_flow_produces_real_heat_load():
    zone = HeatingZone("HZ-FLOW", "R1", "radiator", 45.0, 35.0, 21.0, mass_flow_kg_s=0.1)
    result = MEPEngineeringService().calculate_heating(zone)

    assert result.status == "CALCULATED"
    assert math.isclose(result.values["heat_rate_w"], 4180.0, rel_tol=1e-9)
    assert math.isclose(result.values["heat_rate_kw"], 4.18, rel_tol=1e-9)


def test_load_and_mass_flow_conflict_is_reported():
    zone = HeatingZone(
        "HZ-CONFLICT",
        "R1",
        "underfloor",
        35.0,
        28.0,
        20.0,
        room_heat_load_w=10000.0,
        mass_flow_kg_s=0.5,
    )
    result = MEPEngineeringService().calculate_heating(zone)

    assert result.status == "INPUT_CONFLICT"
    assert "inconsistent" in result.message.lower()
    assert result.values["heat_load_difference_w"] > 0.0


def test_building_engineering_report_aggregates_mep_results():
    model = BuildingModel(name="Report test")
    registry = ensure_mep_registry(model)
    registry.add_ventilation_opening(VentilationOpening("VO-1", "R1", "supply", 0.1, 0.05))
    registry.add_water_branch(WaterBranch("WB-1", "R1", "cold_water", 0.02, 0.0002, length_m=5.0))
    registry.add_heating_zone(HeatingZone("HZ-1", "R1", "underfloor", 35.0, 28.0, 20.0, room_heat_load_w=10000.0))

    report = build_building_engineering_report(model)

    assert report.status == "CALCULATED"
    assert report.result_count == 3
    assert report.calculated_count == 3
    assert report.input_required_count == 0
    assert report.total_ventilation_flow_m3_h > 0.0
    assert math.isclose(report.total_heating_load_w, 10000.0, rel_tol=1e-9)
    assert report.total_water_pressure_drop_pa >= 0.0
    assert model.building_engineering_report == report


def test_building_engineering_report_marks_missing_heating_input():
    model = BuildingModel(name="Incomplete report")
    registry = ensure_mep_registry(model)
    registry.add_heating_zone(HeatingZone("HZ-EMPTY", "R1", "underfloor", 35.0, 28.0, 20.0))

    report = build_building_engineering_report(model)

    assert report.status == "INPUT_REQUIRED"
    assert report.input_required_count == 1
    assert report.total_heating_load_w == 0.0
