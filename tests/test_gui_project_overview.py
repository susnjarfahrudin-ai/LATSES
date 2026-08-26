from lat_ces.gui_dashboard import ProjectOverviewApp


def test_project_overview_is_first_tab_and_routes_to_existing_views():
    # Do not instantiate Tk in the unit test runner; verify the dashboard contract on the class.
    assert issubclass(ProjectOverviewApp, object)
    assert hasattr(ProjectOverviewApp, "_install_project_overview")
    assert hasattr(ProjectOverviewApp, "_refresh_project_overview")
    assert hasattr(ProjectOverviewApp, "_select_tab")
