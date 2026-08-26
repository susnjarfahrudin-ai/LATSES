from lat_ces.building.mep import UnderfloorHeatingCircuit, ensure_mep_registry
from lat_ces.building.underfloor_routing import route_room_serpentine
from lat_ces.reference_house_workflow import build_reference_house_workflow


def test_routed_path_can_be_stored_as_canonical_underfloor_circuit() -> None:
    workflow = build_reference_house_workflow()
    model = workflow.model
    level = next(iter(model.levels.values()))
    room = next(iter(level.rooms.values()))
    route = route_room_serpentine(room, spacing_m=0.15)

    circuit = UnderfloorHeatingCircuit(
        id="UFH-CIRCUIT-1",
        room_id=room.room_id,
        level_id=level.level_id,
        pipe_product_id="UFH-PEX-16X2",
        spacing_m=route.spacing_m,
        path_points_m=route.points_m,
        length_m=route.length_m,
        design_supply_temp_c=35.0,
        design_return_temp_c=30.0,
    )
    registry = ensure_mep_registry(model)
    registry.add_underfloor_circuit(circuit)

    stored = registry.all_underfloor_circuits[-1]
    assert stored.path_points_m == route.points_m
    assert stored.length_m == route.length_m
    assert model.mep is registry
