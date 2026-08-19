from dataclasses import replace

from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building.model import BuildingModel
from lat_ces.building_model.systems import HeatingZone


def test_building_model_owns_heating_zone_registry():
    model = BuildingModel(name="Heating test")
    registry = ensure_mep_registry(model)
    zone = HeatingZone("HZ-1", "ROOM-1", "underfloor", 35.0, 28.0, 20.0)
    registry.add_heating_zone(zone)
    assert ensure_mep_registry(model) is registry
    assert registry.all_heating_zones == (zone,)


def test_heating_zone_can_be_updated_and_removed():
    model = BuildingModel(name="Heating edit")
    registry = ensure_mep_registry(model)
    zone = HeatingZone("HZ-2", "ROOM-2", "radiator", 45.0, 35.0, 21.0)
    registry.add_heating_zone(zone)

    updated = registry.update_heating_zone(
        zone.id,
        emitter_type="underfloor",
        design_supply_temp_c=35.0,
        design_return_temp_c=28.0,
    )
    assert updated.emitter_type == "underfloor"
    assert updated.design_supply_temp_c == 35.0
    assert updated.design_return_temp_c == 28.0
    assert registry.heating_zones[zone.id] == replace(
        zone,
        emitter_type="underfloor",
        design_supply_temp_c=35.0,
        design_return_temp_c=28.0,
    )

    removed = registry.remove_heating_zone(zone.id)
    assert removed.id == zone.id
    assert registry.all_heating_zones == ()


def test_heating_zone_rejects_non_descending_temperatures():
    import pytest

    with pytest.raises(ValueError, match="supply temperature"):
        HeatingZone("HZ-3", "ROOM-3", "underfloor", 28.0, 35.0, 20.0)


def test_heating_gui_module_imports_without_creating_a_window():
    from lat_ces.gui_heating import HeatingMEPDraftingApp

    assert HeatingMEPDraftingApp.__name__ == "HeatingMEPDraftingApp"
