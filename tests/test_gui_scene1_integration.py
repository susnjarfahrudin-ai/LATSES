from pathlib import Path

from lat_ces.gui_scene1 import Scene1CompleteBuildingWorkspaceApp


def test_scene1_gui_reuses_existing_workspace_and_controller():
    assert Scene1CompleteBuildingWorkspaceApp.__mro__[1].__name__ == "CompleteBuildingWorkspaceApp"
    assert "_presentation_controller" in Scene1CompleteBuildingWorkspaceApp.__init__.__code__.co_names
    assert "present_scene_1" in Scene1CompleteBuildingWorkspaceApp.show_scene1.__code__.co_names


def test_default_gui_entry_points_to_scene1_wrapper():
    text = Path("pyproject.toml").read_text(encoding="utf-8")
    assert 'lat-ces-gui = "lat_ces.gui_scene1:main"' in text
