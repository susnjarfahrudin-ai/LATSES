from lat_ces.gui_product_catalog import ProductCatalogMixin
from lat_ces.gui_presentation import Scene2PresentationExtension
from lat_ces.gui_scene1 import Scene1CompleteBuildingWorkspaceApp
from lat_ces.scene1_gui_mixin import Scene1GUIMixin
from lat_ces.gui_architecture.adapters import ThreeDHandoffAdapter


def test_scene1_exposes_external_3d_blender_handoff():
    assert "export_scene3d_to_blender" in Scene1GUIMixin.__dict__
    names = Scene1GUIMixin.export_scene3d_to_blender.__code__.co_names
    assert "_three_d_handoff_adapter" in names
    assert hasattr(Scene1CompleteBuildingWorkspaceApp, "export_scene3d_to_blender")
    assert ThreeDHandoffAdapter.status.value == "CONNECTED"


def test_main_gui_exposes_material_and_3d_actions():
    install = Scene1CompleteBuildingWorkspaceApp._install_scene1_control
    names = install.__code__.co_names
    assert "_open_material_input" not in names
    assert any(
        "_set_view_step" in getattr(const, "co_names", ())
        for const in install.__code__.co_consts
        if hasattr(const, "co_names")
    )
    assert "export_scene3d_to_blender" in names
    assert "_install_product_catalog_tab" in Scene1CompleteBuildingWorkspaceApp.__dict__ or hasattr(
        Scene1CompleteBuildingWorkspaceApp, "_install_product_catalog_tab"
    )
    assert issubclass(Scene1CompleteBuildingWorkspaceApp, ProductCatalogMixin)


def test_catalog_material_action_is_owned_by_catalog_mixin() -> None:
    names = ProductCatalogMixin._install_product_catalog_tab.__code__.co_names
    assert "_open_catalog_material_input" in names
    assert "Novi materijal" not in Scene1CompleteBuildingWorkspaceApp._install_scene1_control.__code__.co_consts
