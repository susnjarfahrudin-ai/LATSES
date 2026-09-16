from lat_ces.gui_complete import CompleteBuildingWorkspaceApp, show_canonical_model_inspector


def test_gui_launcher_exposes_canonical_model_inspector():
    assert callable(show_canonical_model_inspector)
    assert CompleteBuildingWorkspaceApp._build_model_tab.__module__ == "lat_ces.gui_complete"
    assert hasattr(CompleteBuildingWorkspaceApp, "show_canonical_model_inspector")
