from lat_ces.gui_product_catalog import ProductCatalogMixin
from lat_ces.gui_scene1 import Scene1CompleteBuildingWorkspaceApp


def test_scene1_exposes_external_3d_blender_handoff() -> None:
    assert "export_scene3d_to_blender" in Scene1CompleteBuildingWorkspaceApp.__dict__
    assert "write_blender_exchange" in Scene1CompleteBuildingWorkspaceApp.export_scene3d_to_blender.__code__.co_names


def test_main_gui_exposes_catalog_material_and_3d_actions() -> None:
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
