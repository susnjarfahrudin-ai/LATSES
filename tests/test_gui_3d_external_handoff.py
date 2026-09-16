from lat_ces.gui_scene1 import Scene1CompleteBuildingWorkspaceApp


def test_scene1_exposes_external_3d_blender_handoff() -> None:
    assert "export_scene3d_to_blender" in Scene1CompleteBuildingWorkspaceApp.__dict__
    assert "write_blender_exchange" in Scene1CompleteBuildingWorkspaceApp.export_scene3d_to_blender.__code__.co_names


def test_main_gui_exposes_material_and_3d_actions() -> None:
    install = Scene1CompleteBuildingWorkspaceApp._install_scene1_control
    names = install.__code__.co_names
    assert "_open_material_input" in names
    assert "_set_view_step" in names
    assert "export_scene3d_to_blender" in names
