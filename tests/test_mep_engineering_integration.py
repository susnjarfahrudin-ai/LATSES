from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building.mep_engineering import MEPEngineeringService, ensure_engineering_results
from lat_ces.building.model import BuildingModel
from lat_ces.building_model.systems import HeatingZone, VentilationOpening, WaterBranch


def test_ventilation_selection_runs_engine_and_stores_result():
    model = BuildingModel(name="MEP engineering")
    registry = ensure_mep_registry(model)
    opening = VentilationOpening("VO-1", "R1", "supply", 0.1, 0.05)
    registry.add_ventilation_opening(opening)

    result = MEPEngineeringService().calculate("ventilation", opening)
    ensure_engineering_results(registry).put(result)

    assert result.status == "CALCULATED"
    assert result.values["design_flow_m3_h"] > 0.0
    assert ensure_engineering_results(registry).get("ventilation", "VO-1") == result


def test_water_selection_runs_darcy_weisbach_calculation():
    branch = WaterBranch("WB-1", "R1", "cold_water", 0.02, 0.0002, length_m=5.0)
    result = MEPEngineeringService().calculate("water", branch)

    assert result.status == "CALCULATED"
    assert result.values["velocity_m_s"] > 0.0
    assert result.values["reynolds"] > 0.0
    assert result.values["pressure_drop_pa"] >= 0.0


def test_heating_selection_requires_real_flow_or_heat_load_instead_of_assuming_one():
    zone = HeatingZone("HZ-1", "R1", "underfloor", 35.0, 28.0, 20.0)
    result = MEPEngineeringService().calculate("heating", zone)

    assert result.status == "INPUT_REQUIRED"
    assert result.values["design_delta_t_k"] == 7.0
    assert result.values["required_input"] == "mass_flow_kg_s or room_heat_load_w"


def test_engineering_gui_module_imports_without_creating_a_window():
    from lat_ces.gui_mep_engineering import EngineeringMEPWorkspaceApp

    assert EngineeringMEPWorkspaceApp.__name__ == "EngineeringMEPWorkspaceApp"
