from lat_ces.gui_scene1 import Scene1CompleteBuildingWorkspaceApp


def test_scene1_exposes_external_3d_blender_handoff() -> None:
    assert "export_scene3d_to_blender" in Scene1CompleteBuildingWorkspaceApp.__dict__
    assert "write_blender_exchange" in Scene1CompleteBuildingWorkspaceApp.export_scene3d_to_blender.__code__.co_names
