from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building.model import BuildingModel
from lat_ces.building_model.systems import HeatingZone, VentilationOpening, WaterBranch


def test_unified_mep_registry_exposes_all_three_object_types():
    model = BuildingModel(name="Unified MEP")
    registry = ensure_mep_registry(model)
    registry.add_ventilation_opening(
        VentilationOpening(
            id="VO-1",
            room_id="R1",
            kind="supply",
            diameter_m=0.10,
            design_velocity_m_s=0.05,
            elevation_m=0.70,
            x_m=1.0,
            y_m=1.0,
        )
    )
    registry.add_water_branch(
        WaterBranch(
            id="WB-1",
            room_id="R1",
            service="cold_water",
            diameter_m=0.02,
            design_flow_m3_s=0.0002,
            length_m=2.0,
            x1_m=1.0,
            y1_m=1.0,
            x2_m=3.0,
            y2_m=1.0,
        )
    )
    registry.add_heating_zone(
        HeatingZone("HZ-1", "R1", "underfloor", 35.0, 28.0, 20.0)
    )

    assert tuple(item.id for item in registry.all_ventilation_openings) == ("VO-1",)
    assert tuple(item.id for item in registry.all_water_branches) == ("WB-1",)
    assert tuple(item.id for item in registry.all_heating_zones) == ("HZ-1",)


def test_unified_mep_workspace_imports_without_creating_a_window():
    from lat_ces.gui_mep_workspace import UnifiedMEPWorkspaceApp

    assert UnifiedMEPWorkspaceApp.__name__ == "UnifiedMEPWorkspaceApp"
