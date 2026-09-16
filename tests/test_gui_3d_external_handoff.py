from lat_ces.gui_scene1 import Scene1CompleteBuildingWorkspaceApp
from lat_ces.scene1_gui_mixin import Scene1GUIMixin


def test_scene1_exposes_external_3d_blender_handoff() -> None:
    assert "export_scene3d_to_blender" in Scene1GUIMixin.__dict__
    assert "write_blender_exchange" in Scene1GUIMixin.export_scene3d_to_blender.__code__.co_names
    assert hasattr(Scene1CompleteBuildingWorkspaceApp, "export_scene3d_to_blender")


def test_main_gui_exposes_material_and_3d_actions() -> None:
    install = Scene1CompleteBuildingWorkspaceApp._install_scene1_control
    names = install.__code__.co_names
    assert "_open_material_input" in names
    assert any(
        "_set_view_step" in getattr(const, "co_names", ())
        for const in install.__code__.co_consts
        if hasattr(const, "co_names")
    )
    assert "export_scene3d_to_blender" in names
