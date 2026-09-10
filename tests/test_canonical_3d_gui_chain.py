from math import isclose

from lat_ces.building.geometry3d import build_geometry
from lat_ces.building.model import BuildingModel
from lat_ces.building.workflow import BuildingWorkflow, make_square_floor_plan
from lat_ces.visualization_3d_adapter import to_building_scene_3d


def test_gui_geometry_is_projected_from_canonical_scene_and_preserves_roof():
    model = BuildingModel(name="3-D canonical chain")
    workflow = BuildingWorkflow(model=model)
    workflow.set_floor_plan(make_square_floor_plan("Prizemlje", 10.0))
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
    scene_walls = [item for item in scene.objects if item.element_type == "wall"]
    scene_roofs = [item for item in scene.objects if item.element_type == "roof"]
    geometries = build_geometry(model)

    assert scene_walls
    assert len(scene_roofs) == 1
    assert len(geometries) == len(model.levels)
    assert len(geometries[0].walls) == len(scene_walls)

    first_scene_wall = scene_walls[0]
    first_gui_wall = geometries[0].walls[0]
    assert first_gui_wall.wall_id == first_scene_wall.source_element_id
    assert isclose(first_gui_wall.x1, first_scene_wall.geometry.origin_x_m)
    assert isclose(first_gui_wall.y1, first_scene_wall.geometry.origin_y_m)
    assert isclose(first_gui_wall.length, first_scene_wall.geometry.length_m)
    assert isclose(first_gui_wall.thickness, first_scene_wall.geometry.width_m)
    assert isclose(first_gui_wall.height, first_scene_wall.geometry.height_m)

    roof = model.roof
    scene_roof = scene_roofs[0]
    assert roof is not None
    assert scene_roof.source_element_id == roof.roof_id
    assert scene_roof.material_ref == roof.covering
    assert scene_roof.name == roof.roof_type
    assert scene_roof.geometry.length_m == roof.length_m
    assert scene_roof.geometry.width_m == roof.width_m
    assert scene_roof.geometry.height_m == roof.height_m
