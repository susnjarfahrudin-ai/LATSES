"""Integration checkpoint for the canonical BuildingModel engineering path."""

from pathlib import Path


def test_canonical_building_engineering_surface_is_present():
    """Keep the active engineering/build path tied to the canonical workspace."""
    root = Path(__file__).resolve().parents[1]
    gui = root / "lat_ces" / "gui_master.py"
    catalog = root / "lat_ces" / "materials" / "building_materials.catalog.json"
    reference = root / "lat_ces" / "reference_house_model.json"

    assert gui.is_file()
    source = gui.read_text(encoding="utf-8")
    assert "MasterBuildingWorkspaceApp" in source
    assert "self.complete_tabs" in source
    assert catalog.is_file()
    assert reference.is_file()
