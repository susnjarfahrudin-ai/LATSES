from lat_ces.gui_product_engineering_dashboard import ProductEngineeringWorkspaceApp
from lat_ces.scene1_gui_mixin import Scene1GUIMixin


def test_production_gui_entrypoint_includes_scene1_boundary():
    """The packaged GUI class must expose the canonical Scene 1 consumer."""
    assert issubclass(ProductEngineeringWorkspaceApp, Scene1GUIMixin)
    assert callable(ProductEngineeringWorkspaceApp.show_scene1)
    assert callable(ProductEngineeringWorkspaceApp.export_scene3d_to_blender)
