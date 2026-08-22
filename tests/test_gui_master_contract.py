from lat_ces.gui_master import MasterBuildingWorkspaceApp


def test_master_command_callbacks_exist():
    required = (
        "_load_reference_house",
        "_show_view",
        "_run_master_validation",
        "_show_engineering_report",
        "_refresh_master_metrics",
        "_refresh_level_selector",
        "_install_catalog_tab",
        "_refresh_catalog_view",
        "_show_catalog_selection",
    )
    for name in required:
        assert callable(getattr(MasterBuildingWorkspaceApp, name, None)), name


def test_reference_house_loader_is_canonical_workflow_entrypoint():
    method = MasterBuildingWorkspaceApp._load_reference_house
    assert "build_reference_house_workflow" in method.__code__.co_names


def test_catalog_tab_uses_canonical_complete_tabs_container():
    method = MasterBuildingWorkspaceApp._install_catalog_tab
    names = set(method.__code__.co_names)
    assert "complete_tabs" in names
    assert "tabs" in names  # legacy fallback only
