from lat_ces.building.engineering_report import build_building_engineering_report
from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building.reference_house_project import build_reference_house_workflow
from lat_ces.building.electrical import ensure_electrical_registry
from lat_ces.reference_house import ReferenceHouse


def test_reference_house_exercises_canonical_building_engineering_pipeline():
    house = ReferenceHouse.default()
    workflow = build_reference_house_workflow()
    model = workflow.model

    assert len(model.levels) == 3
    assert [level.name for level in model.levels.values()] == ["Prizemlje", "Sprat 1", "Sprat 2"]
    assert model.roof is not None
    assert model.roof.slope_deg == 35.0
    assert sum(len(level.rooms) for level in model.levels.values()) == len(house.conditioned_rooms)

    registry = ensure_mep_registry(model)
    assert len(registry.all_ventilation_openings) == 10
    assert len(registry.all_water_branches) == 8
    assert len(registry.all_heating_zones) == 16

    electrical = ensure_electrical_registry(model)
    assert electrical.loads

    report = build_building_engineering_report(model)

    assert report.status == "CALCULATED"
    assert report.result_count == 34
    assert report.calculated_count == 34
    assert report.input_required_count == 0
    assert report.conflict_count == 0
    assert report.total_ventilation_flow_m3_h > 0.0
    assert report.total_heating_load_w > 0.0
    assert report.total_water_pressure_drop_pa > 0.0
    assert report.electrical.status == "CALCULATED"
    assert report.quantities.floor_area_m2 > 0.0
    assert report.thermal.status == "CALCULATED"


def test_reference_house_cooling_remains_explicit_until_a_canonical_cooling_solver_exists():
    house = ReferenceHouse.default()
    cooling = house.data["cooling"]
    assert cooling["method"]
    assert cooling["design_supply_c"] == 18.0
    assert cooling["design_return_c"] == 21.0
