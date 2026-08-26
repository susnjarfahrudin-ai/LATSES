from lat_ces.building_model.systems import HeatingZone, VentilationOpening, WaterBranch
from lat_ces.mep import to_mep_view


def test_mep_view_preserves_canonical_identity_and_room_link():
    ventilation = VentilationOpening("vent-1", "room-kitchen", "supply", 0.075)
    water = WaterBranch("water-1", "room-kitchen", "cold_water", 0.02, 0.0002)
    heating = HeatingZone("heat-1", "room-kitchen", "underfloor", 35.0, 30.0)

    view = to_mep_view((ventilation, water, heating))

    assert [item.element_id for item in view.elements] == ["vent-1", "water-1", "heat-1"]
    assert all(item.room_id == "room-kitchen" for item in view.elements)
    assert {item.kind for item in view.elements} == {
        "VentilationOpening", "WaterBranch", "HeatingZone"
    }
    assert len(view.for_room("room-kitchen")) == 3


def test_mep_view_is_immutable_and_does_not_redefine_domain_objects():
    ventilation = VentilationOpening("vent-1", "room-kitchen", "supply", 0.075)
    view = to_mep_view((ventilation,))

    try:
        view.elements[0].element_id = "other"
    except Exception:
        pass
    else:
        raise AssertionError("MEP scientific views must be immutable")

    assert ventilation.id == "vent-1"
