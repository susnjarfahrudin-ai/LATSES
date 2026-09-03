from lat_ces.building.mep import HeatingZone, UnderfloorHeatingSystem, ensure_mep_registry
from lat_ces.gui_mep_engineering import EngineeringMEPWorkspaceApp
from lat_ces.reference_house_workflow import build_reference_house_workflow


def test_mep_engineering_entrypoint_is_available() -> None:
    assert EngineeringMEPWorkspaceApp.__name__ == "EngineeringMEPWorkspaceApp"


def test_mep_objects_stay_in_canonical_building_model_registry() -> None:
    workflow = build_reference_house_workflow()
    model = workflow.model
    registry = ensure_mep_registry(model)

    level = next(iter(model.levels.values()))
    room = next(iter(level.rooms.values()))

    zone = HeatingZone(
        id="HZ-CONTRACT-1",
        room_id=room.room_id,
        emitter_type="underfloor",
        source_type="heat_pump_air_water",
        design_supply_temp_c=35.0,
        design_return_temp_c=30.0,
        room_heat_load_w=1200.0,
    )
    registry.add_heating_zone(zone)

    system = UnderfloorHeatingSystem(
        id="UFH-CONTRACT-1",
        room_id=room.room_id,
        level_id=level.level_id,
        pipe_product_id="UFH-PEX-16X2",
        pipe_spacing_m=0.15,
        insulation_product_id="INSULATION-EPS",
        insulation_thickness_m=0.05,
        screed_thickness_m=0.05,
        finish_thickness_m=0.01,
        source_type="heat_pump_air_water",
        target_indoor_temp_c=20.0,
        design_supply_temp_c=35.0,
        design_return_temp_c=30.0,
    )
    registry.add_underfloor_system(system)

    assert model.mep is registry
    assert registry.all_heating_zones[-1].room_id == room.room_id
    assert registry.all_underfloor_systems[-1].level_id == level.level_id
