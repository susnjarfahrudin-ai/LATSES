from lat_ces.building.elements import Stair, Terrace
from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.reference_house_workflow import build_reference_house_workflow


def test_reference_house_populates_stair_and_terrace():
    workflow = build_reference_house_workflow()
    levels = list(workflow.model.levels.values())
    stairs = [stair for level in levels for stair in level.stairs.values()]
    terraces = [terrace for level in levels for terrace in level.terraces.values()]

    assert len(stairs) == 1
    assert stairs[0].riser_count == 16
    assert stairs[0].riser_height_m == 0.175
    assert stairs[0].tread_width_m == 0.28
    assert stairs[0].landing is True
    assert stairs[0].railing is True
    assert stairs[0].floor_opening is True
    assert abs(stairs[0].plan_area_m2 - 10.0) < 1e-9

    assert len(terraces) == 1
    assert abs(terraces[0].plan_area_m2 - 12.0) < 1e-9
    assert terraces[0].construction_type == "betonska konstrukcija"


def test_stair_and_terrace_are_canonical_geometry_objects():
    stair = Stair("Stepenište", Box3D(Point3D(0, 0, 0), 5, 2, 2.8))
    terrace = Terrace("Terasa", Box3D(Point3D(1, 1, 0), 4, 3, 0.2))
    assert stair.id.startswith("STAIR:")
    assert terrace.id.startswith("TERRACE:")
    assert stair.footprint.floor_area == 10.0
    assert terrace.footprint.floor_area == 12.0
