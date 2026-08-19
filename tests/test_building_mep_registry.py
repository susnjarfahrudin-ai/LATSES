from dataclasses import replace

from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building.model import BuildingModel
from lat_ces.building_model.systems import VentilationOpening, WaterBranch


def test_building_model_owns_one_mep_registry():
    model = BuildingModel(name="MEP test")
    registry = ensure_mep_registry(model)
    assert ensure_mep_registry(model) is registry

    opening = VentilationOpening(
        "VO-1",
        "ROOM-1",
        "supply",
        0.10,
        0.05,
        0.70,
        2.0,
        1.5,
    )
    registry.add_ventilation_opening(opening)
    assert registry.all_ventilation_openings == (opening,)


def test_ventilation_opening_can_be_updated_and_removed():
    model = BuildingModel(name="MEP edit")
    registry = ensure_mep_registry(model)
    opening = VentilationOpening("VO-2", "ROOM-2", "extract", 0.10, 0.05, 2.40, 4.0, 3.0)
    registry.add_ventilation_opening(opening)

    updated = registry.update_ventilation_opening(opening.id, diameter_m=0.125, elevation_m=2.50)
    assert updated.diameter_m == 0.125
    assert updated.elevation_m == 2.50
    assert registry.ventilation_openings[opening.id] == replace(opening, diameter_m=0.125, elevation_m=2.50)

    removed = registry.remove_ventilation_opening(opening.id)
    assert removed.id == opening.id
    assert registry.all_ventilation_openings == ()


def test_ventilation_opening_rejects_negative_plan_coordinates():
    import pytest

    with pytest.raises(ValueError, match="coordinates"):
        VentilationOpening("VO-3", "ROOM-3", "supply", 0.10, 0.05, 0.70, -0.1, 1.0)


def test_water_branch_can_be_created_updated_and_removed():
    model = BuildingModel(name="Water MEP test")
    registry = ensure_mep_registry(model)
    branch = WaterBranch(
        "WB-1", "ROOM-1", "cold_water", 0.02, 0.0002, 4.0,
        1.0, 1.0, 4.0, 1.0,
    )
    registry.add_water_branch(branch)
    assert registry.all_water_branches == (branch,)

    updated = registry.update_water_branch(branch.id, diameter_m=0.025, length_m=5.0, x2_m=5.0)
    assert updated.diameter_m == 0.025
    assert updated.length_m == 5.0
    assert updated.x2_m == 5.0

    removed = registry.remove_water_branch(branch.id)
    assert removed.id == branch.id
    assert registry.all_water_branches == ()


def test_water_branch_rejects_negative_plan_coordinates():
    import pytest

    with pytest.raises(ValueError, match="coordinates"):
        WaterBranch("WB-2", "ROOM-2", "dhw", 0.02, 0.0002, 2.0, -0.1, 1.0, 2.0, 1.0)


def test_mep_gui_modules_import_without_creating_a_window():
    from lat_ces.gui_mep import MEPEnabledDraftingApp
    from lat_ces.gui_water import WaterMEPDraftingApp

    assert MEPEnabledDraftingApp.__name__ == "MEPEnabledDraftingApp"
    assert WaterMEPDraftingApp.__name__ == "WaterMEPDraftingApp"
