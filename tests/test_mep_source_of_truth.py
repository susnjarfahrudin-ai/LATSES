from lat_ces.building.mep import HeatingZone, VentilationOpening, WaterBranch, ensure_mep_registry
from lat_ces.building.model import BuildingModel
from lat_ces.mep import to_building_mep_view, to_mep_view


def test_mep_view_preserves_canonical_identity_and_room_link():
    model = BuildingModel("Reference House")
    registry = ensure_mep_registry(model)
    registry.add_ventilation_opening(VentilationOpening("vent-1", "room-kitchen", "supply", 0.075))
    registry.add_water_branch(WaterBranch("water-1", "room-kitchen", "cold_water", 0.02, 0.0002))
    registry.add_heating_zone(HeatingZone("heat-1", "room-kitchen", "underfloor", 35.0, 30.0))

    view = to_building_mep_view(model)
    assert [item.element_id for item in view.elements] == ["vent-1", "water-1", "heat-1"]
    assert all(item.room_id == "room-kitchen" for item in view.elements)
    assert len(view.for_room("room-kitchen")) == 3


def test_mep_view_is_immutable():
    ventilation = VentilationOpening("vent-1", "room-kitchen", "supply", 0.075)
    view = to_mep_view((ventilation,))
    try:
        view.elements[0].element_id = "other"
    except Exception:
        pass
    else:
        raise AssertionError("MEP scientific views must be immutable")
    assert ventilation.id == "vent-1"
