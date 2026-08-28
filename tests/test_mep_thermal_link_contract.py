from lat_ces.reference_house_workflow import build_reference_house_workflow
from lat_ces.mep.thermal_link import apply_thermal_room_loads_to_heating_zones
from lat_ces.building.mep import HeatingZone, ensure_mep_registry


def test_reference_house_uses_canonical_lambda_for_mep() -> None:
    workflow = build_reference_house_workflow()
    registry = ensure_mep_registry(workflow.model)
    room = next(iter(next(iter(workflow.model.levels.values())).rooms.values()))
    registry.add_heating_zone(
        HeatingZone(
            id="HZ-REFERENCE-TEST",
            room_id=room.room_id,
            emitter_type="underfloor",
            design_supply_temp_c=35.0,
            design_return_temp_c=30.0,
        )
    )

    results = apply_thermal_room_loads_to_heating_zones(
        workflow.model,
        design_indoor_c=20.0,
        design_outdoor_c=-10.0,
    )

    linked = next(item for item in results if item.zone_id == "HZ-REFERENCE-TEST")
    assert linked.status == "CALCULATED"
    assert linked.room_heat_load_w is not None
    assert linked.room_heat_load_w > 0.0
    assert workflow.model.mep.heating_zones["HZ-REFERENCE-TEST"].room_heat_load_w == linked.room_heat_load_w


def test_reference_house_still_requires_input_when_thermal_result_is_unavailable() -> None:
    workflow = build_reference_house_workflow()
    registry = ensure_mep_registry(workflow.model)
    room = next(iter(next(iter(workflow.model.levels.values())).rooms.values()))
    registry.add_heating_zone(
        HeatingZone(
            id="HZ-MISSING-ROOM",
            room_id="ROOM-NOT-IN-MODEL",
            emitter_type="underfloor",
            design_supply_temp_c=35.0,
            design_return_temp_c=30.0,
        )
    )

    results = apply_thermal_room_loads_to_heating_zones(
        workflow.model,
        design_indoor_c=20.0,
        design_outdoor_c=-10.0,
    )

    linked = next(item for item in results if item.zone_id == "HZ-MISSING-ROOM")
    assert linked.status == "INPUT_REQUIRED"
    assert linked.room_heat_load_w is None
