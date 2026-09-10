"""Minimal integration proof for the production GUI BuildingModel -> canonical 3-D scene."""

from lat_ces.gui import LATCESApp
from lat_ces.building.geometry3d import build_geometry\nfrom lat_ces.visualization_3d_adapter import to_building_scene_3d


def test_production_gui_building_model_projects_to_canonical_3d_without_loss() -> None:
    """Use the exact workflow factory used by LATCESApp, then compare GUI-visible 3-D content."""

    workflow = LATCESApp.new_workflow()
    model = workflow.model

    # Exercise the same production model path used by the GUI and include a roof,
    # because gui.py::draw_3d() renders the roof when it is present.
    workflow.set_roof(
        "Četverovodni",
        2.50,
        construction="Drvena konstrukcija",
        covering="Crijep",
        length_m=10.0,
        width_m=10.0,
        slope_deg=25.0,
    )

    scene = to_building_scene_3d(model)

    assert scene.building_model_id == model.model_id
    assert scene.source_ref == f"building-model:{model.model_id}"

    gui_geometry = []
    for geometry in build_geometry(model):
        gui_geometry.extend(geometry.walls)

    scene_walls = [item for item in scene.objects if item.element_type == "wall"]

    assert len(scene_walls) == len(gui_geometry)

    for gui_wall in gui_geometry:
        scene_wall = next(
            item for item in scene_walls
            if item.source_element_id == gui_wall.wall_id
        )
        assert scene_wall.geometry.length_m == gui_wall.length
        assert scene_wall.geometry.width_m == gui_wall.thickness
        assert scene_wall.geometry.height_m == gui_wall.height

    # The production GUI currently renders a roof in draw_3d() when model.roof exists.
    # The canonical 3-D adapter must not silently lose that GUI-visible element.
    scene_element_types = {item.element_type for item in scene.objects}
    assert model.roof is None or "roof" in scene_element_types
