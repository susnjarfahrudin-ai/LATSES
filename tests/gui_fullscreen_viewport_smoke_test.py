"""Smoke coverage for the engineering-first GUI layout contract."""


def test_gui_master_keeps_engineering_viewport_as_primary_surface():
    from lat_ces import gui_master

    source = gui_master.__file__
    text = open(source, encoding="utf-8").read()
    assert "CompleteBuildingWorkspaceApp" in text
    assert "_load_reference_house" in text


def test_reference_house_workflow_is_available_for_gui_smoke_test():
    from lat_ces.building.reference_house_project import build_reference_house_workflow

    workflow = build_reference_house_workflow()
    assert workflow.model.name
    assert workflow.model.levels
    assert workflow.model.roof is not None
    assert workflow.model.materials
